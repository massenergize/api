from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from task_queue.models import Task

# Create your views here.


def send_greeting():
    print('hello')
    return

def send_dashbord_ready_msg():
    print('You dashboard is redy')
    return

