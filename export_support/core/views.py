from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from .forms import (
    EnquirySubjectChoices,
    EnquirySubjectForm,
    ExportDestinationChoices,
    ExportDestinationForm,
)


class EnquirySubjectFormView(FormView):
    form_class = EnquirySubjectForm
    template_name = "core/enquiry_subject.html"

    def form_valid(self, form):
        enquiry_subject_value = form.cleaned_data["enquiry_subject"]

        only_importing = enquiry_subject_value == [
            EnquirySubjectChoices.IMPORTING_GOODS_TO_THE_UK
        ]
        if only_importing:
            return redirect("core:import-enquiries")

        return redirect("core:export-destination")


class ExportDestinationFormView(FormView):
    form_class = ExportDestinationForm
    template_name = "core/export_destination.html"

    def form_valid(self, form):
        export_destination_value = form.cleaned_data["export_destination"]

        only_exporting_to_eu = export_destination_value == [ExportDestinationChoices.EU]
        if only_exporting_to_eu:
            return redirect(settings.GREAT_CONTACT_FORM)

        return super().form_valid(form)


class ImportEnquiriesView(TemplateView):
    template_name = "core/import_enquiries.html"
