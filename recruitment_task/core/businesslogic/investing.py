from django.shortcuts import get_object_or_404
from core.businesslogic.errors import CannotInvestIntoProjectException
from core.models import Investor, Project


def invest_into_project(investor: Investor, project: Project) -> None:
    """
    Funds project.

    :raises CannotInvestIntoProjectException: If funding criteria were not met.
    """

    if project.funded:
        raise CannotInvestIntoProjectException("Project already funded")

    if investor.remaining_amount < project.amount:
        raise CannotInvestIntoProjectException("Investor has not enough money remaining")

    if investor.individual_amount < project.amount:
        raise CannotInvestIntoProjectException("Investor's individual amount is less than project's amount")

    if investor.project_delivery_deadline < project.delivery_date:
        raise CannotInvestIntoProjectException("Project is not meeting investor's deadline")

    project.funded_by = investor.pk
    project.funded = True
    project.save()

    investor.remaining_amount -= project.amount
    investor.save()
    return