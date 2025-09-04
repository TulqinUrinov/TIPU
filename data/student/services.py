from django.db.models import Value, F, DecimalField, ExpressionWrapper, Sum
from django.db.models.functions import Coalesce, NullIf

from data.student.models import Student


class StudentFilterService:
    @staticmethod
    def filter_students(request, edu_year):
        course = request.query_params.get('course')
        faculty_ids = request.query_params.get('faculty')
        specialization_ids = request.query_params.get('specialization')
        percentage_range = request.query_params.get('percentage')
        type_filter = request.query_params.get('type')
        status = request.query_params.get('status')
        education_form = request.query_params.get('education_form')

        queryset = Student.objects.filter(
            student_years__education_year_id=edu_year
        ).annotate(
            contract_amount=Coalesce(
                F("contract__period_amount_dt"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            left=Coalesce(
                Sum("contract_payments__left"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
        ).annotate(
            total_paid=F("contract_amount") - F("left"),
            percentage=ExpressionWrapper(
                (F("total_paid") * Value(100, output_field=DecimalField()))
                / NullIf(F("contract_amount"), Value(0, output_field=DecimalField())),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        )

        # Kurs bo‘yicha filter
        if course:
            queryset = queryset.filter(course=course)

        # Student statusi bo'yicha filter
        if status:
            queryset = queryset.filter(status=status)

        if education_form:
            queryset = queryset.filter(education_form=education_form)

        # Fakultet bo‘yicha filter
        if faculty_ids:
            faculty_list = [int(f_id) for f_id in faculty_ids.split(",")]
            queryset = queryset.filter(specialization__faculty_id__in=faculty_list)

        # Yo'nalishi bo'yicha filter
        if specialization_ids:
            specialization_list = [int(s_id) for s_id in specialization_ids.split(",")]
            queryset = queryset.filter(specialization_id__in=specialization_list)

        # HEMIS / NO-HEMIS bo‘yicha filter
        if type_filter == "hemis":
            queryset = queryset.filter(user_account__isnull=True)
        if type_filter == "no-hemis":
            queryset = queryset.filter(user_account__isnull=False)

        # percentage bo‘yicha filter
        if percentage_range:
            if "-" in percentage_range:
                start, end = map(float, percentage_range.split("-"))
                queryset = queryset.filter(
                    percentage__gte=start,
                    percentage__lte=end
                )
            else:
                value = float(percentage_range)
                queryset = queryset.filter(percentage=value)

        return queryset.distinct()
