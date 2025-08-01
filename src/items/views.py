import s3
import pathlib
import mimetypes
from cfehome.env import config
# from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required as login_required
from django.http import QueryDict, HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse 
from projects import cache as projects_cache
from projects.decorators import project_required
from django.utils.text import slugify
from django.core.cache import cache
from django.views.decorators.cache import cache_control

from django_htmx.http import HttpResponseClientRedirect

from cfehome import http

from . import forms
from .models import Item


AWS_ACCESS_KEY_ID=config("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY=config("AWS_SECRET_ACCESS_KEY", default=None)
AWS_BUCKET_NAME=config("AWS_BUCKET_NAME", default=None)
AWS_ENDPOINT_URL=config("AWS_ENDPOINT_URL", default="http://minio:9000")
AWS_PUBLIC_ENDPOINT_URL=config("AWS_PUBLIC_ENDPOINT_URL", default=None)




def filename_to_s3_filename(fname):
    if fname is None:
        return None
    if fname == '':
        return None
    stem = pathlib.Path(fname).stem
    suffix = pathlib.Path(fname).suffix
    stem_clean = slugify(stem).replace('-', '_')
    return f'{stem_clean}{suffix}'

@project_required
@login_required
def item_upload_view(request, id=None):
    instance = get_object_or_404(Item, id=id, project=request.project)
    # if not request.htmx:
    #     detail_url = instance.get_absolute_url()
    #     return redirect(detail_url)
    template_name = 'items/file-upload.html'
    if request.htmx:
        template_name = 'items/snippets/upload.html'
    if request.method == "POST":
        print(request.POST)
        file_name = request.POST.get('file_name')
        name = filename_to_s3_filename(file_name)
        if name is None:
            """
            Invalid name, alert user
            """
            return JsonResponse({"url": None})
        
        # Validate S3 configuration
        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME, AWS_ENDPOINT_URL]):
            print(f"S3 Config Error in upload - Access Key: {AWS_ACCESS_KEY_ID is not None}, Secret Key: {AWS_SECRET_ACCESS_KEY is not None}, Bucket: {AWS_BUCKET_NAME is not None}, Endpoint: {AWS_ENDPOINT_URL is not None}")
            return JsonResponse({"url": None, "error": "S3 configuration error"})
        
        try:
            s3_client = s3.S3Client(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                default_bucket_name=AWS_BUCKET_NAME,
                endpoint_url=AWS_ENDPOINT_URL,
                public_endpoint_url=AWS_PUBLIC_ENDPOINT_URL,
            )
            prefix = instance.get_prefix()
            key = f"{prefix}{name}"
            url = s3_client.generate_presigned_url_with_public_endpoint('put_object', {"Bucket": AWS_BUCKET_NAME, "Key": key}, 3600)
            return JsonResponse({"url": url, 'filename': name})
        except Exception as e:
            print(f"S3 Upload presign error: {e}")
            return JsonResponse({"url": None, "error": str(e)})
    return render(request, template_name, 
                    {
                     "instance": instance}
                )


@project_required
@login_required
def item_file_delete_view(request, id=None, name=None):
    instance = get_object_or_404(Item, id=id, project=request.project)
    if not request.htmx:
        detail_url = instance.get_absolute_url()
        return redirect(detail_url)
    if request.method != "POST":
        detail_url = instance.get_absolute_url()
        return HttpResponseClientRedirect(detail_url)
    # modal for a confirm file name
    prefix = instance.get_prefix()
    client = s3.S3Client(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        default_bucket_name=AWS_BUCKET_NAME,
        endpoint_url=AWS_ENDPOINT_URL,
        public_endpoint_url=AWS_PUBLIC_ENDPOINT_URL,
    ).client
    prefix = instance.get_prefix()
    key = f"{prefix}{name}"
    if key.endswith("/"):
        key = key[:-1]
    client.delete_object(Bucket=AWS_BUCKET_NAME, Key=key)
    return HttpResponse(f"{name} Deleted")


@project_required
@login_required
def item_files_view(request, id=None):
    instance = get_object_or_404(Item, id=id, project=request.project)
    if not request.htmx:
        detail_url = instance.get_absolute_url()
        return redirect(detail_url)
    template_name = 'items/snippets/object-table.html'
    prefix = instance.get_prefix()
    print(prefix)
    
    # Validate S3 configuration
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME, AWS_ENDPOINT_URL]):
        print(f"S3 Config Error - Access Key: {AWS_ACCESS_KEY_ID is not None}, Secret Key: {AWS_SECRET_ACCESS_KEY is not None}, Bucket: {AWS_BUCKET_NAME is not None}, Endpoint: {AWS_ENDPOINT_URL is not None}")
        return HttpResponse("S3 configuration error. Please check environment variables.", status=500)
    
    try:
        client = s3.S3Client(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            default_bucket_name=AWS_BUCKET_NAME,
            endpoint_url=AWS_ENDPOINT_URL,
            public_endpoint_url=AWS_PUBLIC_ENDPOINT_URL,
        ).client
    except Exception as e:
        print(f"S3 Client creation error: {e}")
        return HttpResponse(f"S3 client error: {str(e)}", status=500)

    try:
        paginator = client.get_paginator("list_objects_v2")
        pag_gen = paginator.paginate(
                Bucket=AWS_BUCKET_NAME,
                Prefix=prefix
        )
        object_list = []
        for page in pag_gen:
            for c in page.get('Contents', []):
                key = c.get('Key')
                size = c.get('Size')
                if size == 0:
                    continue
                name = pathlib.Path(key).name
                _type = None
                try:
                    _type = mimetypes.guess_type(name)[0]
                except:
                    pass
                
                is_image = 'image' in str(_type)
                updated = c.get('LastModified')
                
                # Generate Django URLs instead of S3 presigned URLs
                url = reverse('items:view_file', kwargs={'id': instance.id, 'filename': name})
                download_url = reverse('items:download_file', kwargs={'id': instance.id, 'filename': name})
                
                data = {
                    'key': key,
                    'name': name,
                    'is_image': is_image,
                    'url': url,
                    'download_url': download_url,
                    'type': _type,
                    'size': size,
                    'updated': updated,
                }
                object_list.append(data)
    except Exception as e:
        print(f"S3 List objects error: {e}")
        return HttpResponse(f"S3 list error: {str(e)}", status=500)
    return render(request, template_name, 
                    {'object_list': object_list,
                     "instance": instance}
                )


@project_required
@login_required
def item_list_view(request):
    object_list = Item.objects.filter(project=request.project)
    template_name = "items/list.html"
    if request.htmx:
        template_name = "items/snippets/table.html"
    return render(request, template_name, {'object_list': object_list})


@project_required
@login_required
def item_detail_inline_update_view(request, id=None):
    instance = get_object_or_404(Item, id=id, project=request.project)
    if not request.htmx:
        detail_url = instance.get_absolute_url()
        return redirect(detail_url)
    
    template_name = "items/snippets/table-row-edit.html"
    success_template = "items/snippets/table-row.html"
    if f"{request.method}".lower() == "patch":
        query_dict = QueryDict(request.body)
        data = query_dict.dict()
        form = forms.ItemPatchForm(data)
        if form.is_valid():
            valid_data = form.cleaned_data
            changed = False
            for k, v in valid_data.items():
                changed = True
                if v == "":
                    continue
                if not v:
                    continue
                setattr(instance, k , v)
            if changed:
                instance.save()
        template_name = success_template
        choices = Item.ItemStatus.choices
        context = {
            "instance": instance,
            "choices": choices,
            "form": form,
        }
        return render(request, template_name, context)
    
    form = forms.ItemInlineForm(request.POST or None, instance=instance)
    if form.is_valid():
        item_obj = form.save(commit=False)
        item_obj.last_modified_by = request.user 
        item_obj.save()
        template_name = success_template
    context = {
        "instance": instance,
        "form": form,
    }
    return render(request, template_name, context)


@project_required
@login_required
def item_detail_update_view(request, id=None):
    instance = get_object_or_404(Item, id=id, project=request.project)
    form = forms.ItemUpdateForm(request.POST or None, instance=instance)
    if form.is_valid():
        item_obj = form.save(commit=False)
        item_obj.last_modified_by = request.user 
        item_obj.save()
        return redirect(item_obj.get_absolute_url())
    context = {
        "instance": instance,
        "form": form,
    }
    return render(request, "items/detail.html", context)

@project_required
@login_required
def item_delete_view(request, id=None):
    instance = get_object_or_404(Item, id=id, project=request.project)
    if request.method == "POST":
        instance.delete()
        if request.htmx:
            return http.render_refresh_list_view(request)
        return redirect("items:list")
    return render(request, "items/delete.html", {"instance": instance})


@project_required
@login_required
def item_create_view(request):
    template_name = 'items/create.html'
    if request.htmx:
        template_name = 'items/snippets/form.html'
    form = forms.ItemCreateForm(request.POST or None)
    if form.is_valid():
        item_obj = form.save(commit=False)
        item_obj.project = request.project
        item_obj.added_by = request.user 
        item_obj.save()
        if request.htmx:
            return http.render_refresh_list_view(request)
        return redirect(item_obj.get_absolute_url())
    action_create_url = reverse("items:create")
    context = {
        "form": form,
        "btn_label": "Create item",
        "action_url": action_create_url
    }
    return render(request, template_name, context)


@project_required
@login_required
@cache_control(max_age=3600)  # Cache for 1 hour
def serve_s3_file(request, id=None, filename=None, as_attachment=False):
    instance = get_object_or_404(Item, id=id, project=request.project)
    
    # Create S3 client
    client = s3.S3Client(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        default_bucket_name=AWS_BUCKET_NAME,
        endpoint_url=AWS_ENDPOINT_URL,
    ).client

    # Build the key
    prefix = instance.get_prefix()
    key = f"{prefix}{filename}"
    if key.endswith("/"):
        key = key[:-1]
    
    try:
        # Get the S3 object
        s3_object = client.get_object(Bucket=AWS_BUCKET_NAME, Key=key)
        
        # Get content type
        content_type = s3_object['ContentType']
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # Create response
        response = StreamingHttpResponse(
            s3_object['Body'].iter_chunks(chunk_size=8192),
            content_type=content_type
        )
        
        if as_attachment:
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            
        # Add caching headers
        response['Cache-Control'] = 'max-age=3600'  # 1 hour
        
        return response
        
    except client.exceptions.NoSuchKey:
        raise Http404("File not found")
    except Exception as e:
        return HttpResponse(f"Error accessing file: {str(e)}", status=500)