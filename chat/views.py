from django.shortcuts import render, redirect
from django.http import HttpResponse
from orders.models import Order
from .models import Chat, Message
from notifications.views import NotificationService as sendemail
from accounts.models import Freelancer, Account
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.contrib.auth.decorators import login_required

# Create your views here.
def chat(request):
    return HttpResponse("Hello, World!")

def get_chat_messages(request, chat_id):
    # تأكد من أنك تحقق من صلاحيات المستخدم، وتقوم بفلترة الرسائل بناءً على الدردشة المطلوبة
    messages = Message.objects.filter(chat_id=chat_id).values('content','sender')

    # تحويل الرسائل إلى قائمة من القواميس
    messages_list = list(messages)
    
    # إرجاع البيانات كـ JSON
    return JsonResponse(messages_list, safe=False)

def inbox(request):
    if request.user.account.user_type == 'Customer':
        get_chat = Chat.objects.filter(user= request.user.account)
    elif request.user.account.user_type == 'Freelancer':
        get_chat = Chat.objects.filter(freelancer= request.user.freelancer)
    return render(request, 'accounts/inbox.html' , {'user_chat': get_chat})

def create_chat(request , id_order):
    get_order = Order.objects.get(pk = id_order)
    get_user = Account.objects.get(pk = get_order.customer.id)
    get_freelancer = Freelancer.objects.get(user = request.user)
    get_chat = Chat.objects.filter(user = get_user , freelancer = get_freelancer)
    if get_chat:
        return redirect('chat:inbox' )
    
    save_chat = Chat(user = get_user , freelancer = get_freelancer)
    save_chat.save()
    
    return redirect('chat:inbox' )

def get_chat(request , chat_id):
    get_chat = Chat.objects.get(pk = chat_id)
    get_message = Message.objects.filter(chat =get_chat ).order_by('create_at')
    if request.user.account.user_type == 'Customer':
        all_chat = Chat.objects.filter(user= request.user.account)
    elif request.user.account.user_type == 'Freelancer':
        all_chat = Chat.objects.filter(freelancer= request.user.freelancer)
    
    return render(request , 'accounts/inbox.html' , {'user_chat': all_chat , 'message':get_message , 'sender_user': get_chat})

def send_message(request, chat_id):
    data = json.loads(request.body)
    content = data.get('content')
    chat = Chat.objects.get(id=chat_id)
    Message.objects.create(chat=chat, sender=request.user.account, content=content)
    return JsonResponse({'status': 'Message sent'})

@login_required
def chat_list(request):
    if request.user.account.user_type == 'Customer':
        chats = Chat.objects.filter(user=request.user.account)
    elif request.user.account.user_type == 'Freelancer':
        chats = Chat.objects.filter(freelancer=request.user.freelancer)
    else:
        chats = []
    
    return render(request, 'chat/chat_list.html', {'chats': chats})
