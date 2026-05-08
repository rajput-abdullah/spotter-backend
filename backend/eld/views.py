from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import ELDService


class EldView(APIView):

    def post(self, request):
        trip_details = request.data

        eld_service = ELDService(trip_details)

        result = eld_service.process_trip()

        return Response(result, status=status.HTTP_200_OK)
        

