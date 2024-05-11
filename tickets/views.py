from django.shortcuts import render 
from django.http import JsonResponse

# Create your views here.

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