from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.businesslogic.errors import CannotInvestIntoProjectException
from core.businesslogic.investing import invest_into_project
from core.models import Project, Investor
from core.serializers import ProjectSerializer, ProjectDetailsSerializer, InvestorSerializer, InvestorDetailsSerializer


class ProjectsView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectDetailsView(generics.RetrieveUpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailsSerializer

    def update(self, request, *args, **kwargs):
        project_to_update = self.get_object()
        if project_to_update.funded:
            return Response(data={"details": "Cannot edit funded project."}, status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(project_to_update, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class InvestorsView(generics.ListCreateAPIView):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvestorDetailsView(generics.RetrieveUpdateAPIView):
    queryset = Investor.objects.all()
    serializer_class = InvestorDetailsSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        investor_to_update = self.get_object()
        serializer = self.get_serializer(investor_to_update, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class InvestIntoProject(APIView):
    def post(self, request, pk, project_id):
        investor = get_object_or_404(Investor, pk=pk)
        project_to_invest_into = get_object_or_404(Project, pk=project_id)

        try:
            invest_into_project(investor, project_to_invest_into)
        except CannotInvestIntoProjectException as e:
            return Response(data={"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        investor.refresh_from_db()
        project_to_invest_into.refresh_from_db()
        return Response(
            data={
                "funded_project": ProjectSerializer(instance=project_to_invest_into).data,
                "remaining_amount": investor.remaining_amount
            }, 
            status=status.HTTP_201_CREATED)


class ProjectsForInvestor(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        investor = get_object_or_404(Investor, pk=self.kwargs['pk'])
        queryset = Project.objects.filter(amount__lte=investor.individual_amount,
                                            delivery_date__lte=investor.project_delivery_deadline,
                                            funded=False).filter(amount__lte=investor.remaining_amount)
        return queryset


class InvestorsForProject(generics.ListAPIView):
    serializer_class = InvestorSerializer

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if project.funded:
            Response(data={"details": "This project has been funded."}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Investor.objects.filter(project_delivery_deadline__gte=project.delivery_date,
                                            individual_amount__gte=project.amount,
                                            total_amount__gte=project.amount)
        return queryset