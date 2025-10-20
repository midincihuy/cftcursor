from django import forms

class WhatsAppImportForm(forms.Form):
    json_file = forms.FileField(
        label='WhatsApp JSON File',
        help_text='Upload your exported WhatsApp chat data in JSON format',
        widget=forms.FileInput(attrs={
            'accept': '.json',
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
        })
    )
    
    def clean_json_file(self):
        file = self.cleaned_data.get('json_file')
        if file:
            if not file.name.endswith('.json'):
                raise forms.ValidationError('Please upload a JSON file.')
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('File size must be under 10MB.')
        return file
