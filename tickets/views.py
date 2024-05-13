from django.shortcuts import render 
from django.http.response import JsonResponse 
from .models import Movie, Guest, Reservation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import GuestSerializer, MovieSerializer, ReservationSerializer
from rest_framework import status,filters
from rest_framework.views import APIView  
from rest_framework import generics, mixins,viewsets
from rest_framework.viewsets import ModelViewSet
from django.http import Http404
# Create your views here.

#1 without REST and no model query FBV
def no_rest_no_model(request):
    guests = [
        {
            'id':1,
            'name':'jowan',
            'mobile':5554443322,

        },
        {
            'id':2,
            'name':'ahmed',
            'mobile':5551113322,

        },
        {
            'id':3,
            'name':'omar',
            'mobile':5550003322,

        },
    ]
    return JsonResponse(guests, safe=False)

#2 model data default django without rest
def no_rest_from_model(request):
    data = Guest.objects.all()
    response = {
        'guests': list(data.values('name','mobile'))
    }
    return JsonResponse(response)

# List == GET
# Create == POST
# pk query == GET
# Update == PUT
# Delete destroy == DELETE

#3 Function based views
#3.1 GET POST
@api_view(['GET','POST'])
def FBV_List(request):

    # GET
    if request.method == 'GET':
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)
    # POST
    elif request.method == 'POST':
        serializer = GuestSerializer(data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.data , status= status.HTTP_400_BAD_REQUEST)
    
#3.2 GET PUT DELETE
@api_view(['GET','PUT','DELETE'])
def FBV_pk(request,pk):
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    #GET
    if request.method == 'GET':
        serializer = GuestSerializer(guest, many=False)
        return Response(serializer.data)
    #PUT
    elif request.method == 'PUT':
        serializer = GuestSerializer(guest,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    #DELETE
    elif request.method == 'DELETE':
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
#CBV 
#4.1 List and Create CBV == GET and POST
class CBV_list(APIView):

    def get(self,request):
        guest = Guest.objects.all()
        serializer = GuestSerializer(guest, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data , status=status.HTTP_400_BAD_REQUEST)
    
#4.2 Update , Delete , Detial CBV == PUT , DELETE and PK GET
class CBV_pk(APIView):

    def  get_object(self,pk):
        try :
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Http404
    
    def get(self,request,pk):
        guest = self.get_object(pk)
        serialzer = GuestSerializer(guest, many=False)
        return Response(serialzer.data , status=status.HTTP_200_OK)
    def put(self,request,pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        guest = self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
#5 Mixins
#5.1 mixins list
class mixins_list(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request):
        return self.list(request)
     
    def post(self, request):
        return self.create(request)
    
#5.2 mixins get put delete generic
class mixins_pk(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin,generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
    def get(self, request):
        return self.retrieve(request)
    
    def put(self, request):
        return self.update(request)
    
    def delete(self, request):
        return self.destroy(request)
    
#6 Generics
#6.1 get and post
class generic_list(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

#6.2 get put and delete
class generic_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

#7 viewsets
class viewsets_guest(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class viewsets_movie(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['movies']

class viewsets_reservation(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

#8 Find Movie
@api_view(['GET'])
def find_movie(request):

    movies = Movie.objects.filter(movie__contains= request.data['movie'],hall__contains=request.data['hall'])
    serializer = MovieSerializer(movies , many =True)
    return Response(serializer.data , status=status.HTTP_200_OK)


#9 create new reservation 
@api_view(['POST'])
def new_reservation(request):
    try:
        hall_id = request.data['hall']
        movie_id = request.data['movie']
        guest_name = request.data['name']
        guest_mobile = request.data['mobile']
    except KeyError as e:
        return Response({"error": f"Missing key: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        movie = Movie.objects.get(hall=hall_id, movie=movie_id)
    except Movie.DoesNotExist:
        return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    guest = Guest.objects.create(name=guest_name, mobile=guest_mobile)

    reservation = Reservation.objects.create(guest=guest, movie=movie)

    return Response(status=status.HTTP_201_CREATED)