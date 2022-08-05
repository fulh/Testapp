from import_export.admin import ImportExportModelAdmin,ImportForm,ConfirmImportForm
from django import forms
from .models import CaseInfo

# class CustomImportForm(ImportForm):
#     CaseInfo = forms.ModelChoiceField(
#         queryset=CaseInfo.objects.all(),
#         required=True)
#
# class CustomConfirmImportForm(ConfirmImportForm):
#     CaseInfo = forms.ModelChoiceField(
#         queryset=CaseInfo.objects.all(),
#         required=True)