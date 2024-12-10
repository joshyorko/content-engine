from django import forms
from django.core.validators import RegexValidator
from .models import Project

class ProjectCreateForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Project Title', 'class': 'w-full px-3 py-2 border rounded-lg'}),
        help_text='A descriptive name for your project'
    )
    handle = forms.SlugField(
        widget=forms.TextInput(attrs={'placeholder': 'project-handle', 'class': 'w-full px-3 py-2 border rounded-lg'}),
        help_text='URL-friendly identifier (letters, numbers, hyphens only)'
    )

    class Meta:
        model = Project
        fields = ['title', 'handle']
        
    def clean_handle(self):
        handle = self.cleaned_data.get('handle', '').lower().strip()
        reserved_handles = ['create', 'delete', 'edit', 'update', 'list']
        if handle in reserved_handles:
            raise forms.ValidationError(f"'{handle}' is a reserved word and cannot be used as a handle")
        if not handle.isalnum() and not '-' in handle:
            raise forms.ValidationError("Handle can only contain letters, numbers, and hyphens")
        return handle

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title', '')
        handle = cleaned_data.get('handle', '')
        
        # Check if handle was generated from title
        if handle and title and handle == title.lower().replace(' ', '-'):
            # Ensure handle doesn't exceed max length
            if len(handle) > self.fields['handle'].max_length:
                self.add_error('handle', f'Handle cannot exceed {self.fields["handle"].max_length} characters')
        
        return cleaned_data

class ProjectUpdateForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Project Title', 'class': 'w-full px-3 py-2 border rounded-lg'}),
        help_text='A descriptive name for your project'
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Project Description', 'class': 'w-full px-3 py-2 border rounded-lg', 'rows': 4}),
        help_text='Detailed description of your project',
        required=False
    )
    handle = forms.SlugField(
        widget=forms.TextInput(attrs={'placeholder': 'project-handle', 'class': 'w-full px-3 py-2 border rounded-lg'}),
        help_text='URL-friendly identifier (letters, numbers, hyphens only)'
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'handle']
        
    def clean_handle(self):
        handle = self.cleaned_data.get('handle', '').lower().strip()
        reserved_handles = ['create', 'delete', 'edit', 'update', 'list']
        if handle in reserved_handles:
            raise forms.ValidationError(f"'{handle}' is a reserved word and cannot be used as a handle")
        if not handle.isalnum() and not '-' in handle:
            raise forms.ValidationError("Handle can only contain letters, numbers, and hyphens")
        return handle