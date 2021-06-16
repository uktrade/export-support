from django.views.generic import FormView

from .forms import EnquirySubjectForm


class EnquirySubjectFormView(FormView):
    form_class = EnquirySubjectForm
    template_name = "core/enquiry_subject.html"
