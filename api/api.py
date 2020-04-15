from datetime import datetime
from uuid import uuid4
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import Url
from .serializers import UrlSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction, DatabaseError



class UrlViewSet(viewsets.ViewSet):
    queryset = Url.objects.all()
    serializer_class = UrlSerializer

    def create(self, request):
        serializer = UrlSerializer(data=request.data)
        if serializer.is_valid():
            url = Url.create(url=serializer.data['url'])
            url.save()
            return Response(UrlSerializer(url).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        serializer = UrlSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        url = get_object_or_404(Url, shortened_url=pk)
        return Response(UrlSerializer(url).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def reset(self, request, pk=None):
        url = get_object_or_404(Url, shortened_url=pk)
        url.visits = 0
        url.reset_date = datetime.now()
        url.save()
        return Response(UrlSerializer(url).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def enable(self, request, pk=None):
        url = get_object_or_404(Url, shortened_url=pk)
        if not url.enabled:
            url.enabled = True
            url.disabled_date = None
            url.save()
        return Response(UrlSerializer(url).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def disable(self, request, pk=None):
        url = get_object_or_404(Url, shortened_url=pk)
        if url.enabled:
            url.enabled = False
            url.disabled_date = datetime.now()
            url.save()
        return Response(UrlSerializer(url).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def refresh(self, request, pk=None):
        url = get_object_or_404(Url, shortened_url=pk)
        url.shortened_url = url.generate_short_url(uuid4().node)
        url.save()
        return Response(UrlSerializer(url).data, status=status.HTTP_200_OK)

    def redirect(self, request, shortened_url):
        try:
            url = get_object_or_404(Url, shortened_url=shortened_url)
            with transaction.atomic():
                if not url.enabled:
                    return Response(UrlSerializer(url).data, status=status.HTTP_403_FORBIDDEN)
                url.visits += 1
                url.last_access_date = datetime.now()
                url.save()
        except DatabaseError:
            return Response("Ha ocurrido un problema con la base de datos", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return HttpResponseRedirect(url.url)
