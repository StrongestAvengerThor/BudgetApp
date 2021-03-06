from django.shortcuts import render,redirect
from .form import CustomUserForm, SpendForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout 
from django.utils import timezone
from datetime import datetime
from .calcData import getMonthDetails,allSpendings,getDayDetails

# Create your views here.
def home(request):

    if request.user.is_authenticated:
        if request.method=="GET":  
            date=str(datetime.now())[0:7]
            print(date)
            spendList=request.user.spend_set.all().order_by('-date_added')
            filtered=[]
            for obj in spendList:
                    temp=[]
                    temp.append(obj.spend_id)
                    temp.append(obj.category.category_name)
                    temp.append(obj.amount)
                    temp.append(str(obj.date_added)[0:10])
                    temp.append(obj.comments)
                    filtered.append(temp)

            data=getMonthDetails(filtered,date)

            todaydate=str(datetime.now())[0:10]
            print(todaydate)
            todaydata=getDayDetails(filtered,todaydate)
            print(todaydata)

            header=['Spend_ID','Category','Amount','Spent_On','Comments']    
            
            context={"table":data[0],"header":header,"total":data[1],"count":data[2],"message":"Present Month","categorised":data[3],"eachsum":data[4],"showbar":data[5],"havedetails":data[6],"haveday":todaydata[0],"daysum":todaydata[1],"showguest":False}
            return render(request,"tracker/home.html",context)

        else:
            username=request.user.username
            print(username)

            option=request.POST['view']
            
            date=request.POST[option]
            print(date)
            
            spendList=request.user.spend_set.all()
            filtered=[]
            for obj in spendList:
                    temp=[]
                    temp.append(obj.spend_id)
                    temp.append(obj.category.category_name)
                    temp.append(obj.amount)
                    temp.append(str(obj.date_added)[0:10])
                    temp.append(obj.comments)
                    filtered.append(temp)

            
            header=['Spend_ID','Category','Amount','Spent_On','Comments']    
            data=getMonthDetails(filtered,date)
            if len(data[0])<1:
                message="Looks like there is no spending on this day!"
            else:
                message=f"Spendings for {date}"
            print(data[3])
            context={"showguest":False,"table":data[0],"header":header,"total":data[1],"count":data[2],"message":message,"categorised":data[3],"eachsum":data[4],"showbar":data[5],"havedetails":data[6],"haveday":False,"daysum":0}
            return render(request,"tracker/home.html",context)
    
    else: 
        context={"showguest":False}
        return render(request,"tracker/home.html")


def register(request):

    if request.user.is_authenticated:
        return redirect(reverse("home"))
    
    if request.method=="GET":
        context={"message":"","show":False}
        return render(request,"tracker/register.html",context)

    if request.method=="POST":

        username=request.POST['username']
        password1=request.POST['password1']
        password2=request.POST['password2']

        #print(username,password1,password2)
        checkuser=User.objects.filter(username=username).exists()

        if checkuser:
            message="Whoops! Username Exists..."
            print(message)
            context={"message":message,"show":True}
            return render(request,"tracker/register.html",context)

        else:
            
            if password1==password2:
                print("User saving")
                user=User.objects.create_user(username,None,password1)
                user.save()
                login(request,user)
                return redirect(reverse("home"))
            else:
                message="Whoops! Passwords did not match..."
                context={"message":message,"show":True}
                return render(request,"tracker/register.html",context)


    return redirect(reverse("home"))

def GetSpend(request):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))

    if request.method=="GET":
        context={"form":SpendForm,"error":""}
        return render(request,"tracker/spend.html",context)

    if request.method=="POST":
        form=SpendForm(request.POST)

        if form.is_valid():
            print("valid form for spend")

            #setting it to false so that it doesnt save to DB
            spendObj=form.save(commit=False)
            
            spendObj.user=request.user
            
            spendObj.save()  #now save it to DB
            return redirect(reverse("home"))

        else:
            print("Invalid spend Form submitted")
            context={"form":SpendForm,"error":"Amount should be more than or equals to 0."}
            return render(request,"tracker/spend.html",context)


def ViewSpends(request):
    
    if request.user.is_authenticated:
        spendList=request.user.spend_set.all().order_by('-date_added')

        #spendList=[[obj.spend_id,obj.category.category_name,obj.amount,obj.date_added,obj.comments] for obj in spendList]
        filtered=[]
        for obj in spendList:
            temp=[]
            temp.append(obj.spend_id)
            temp.append(obj.category.category_name)
            temp.append(obj.amount)
            temp.append(str(obj.date_added)[0:10])
            temp.append(obj.comments)

            filtered.append(temp)


        print(filtered)
        data=allSpendings(filtered)
        header=['Spend_ID','Category','Amount','Spent_On','Comments']
        context={"table":data[0],"header":header,"total":data[1],"count":data[2],"message":"All Expenditure till now...","categorised":data[3],"eachsum":data[4],"havedetails":data[5]}

        #context={"table":filtered,"header":header}
        return render(request,"tracker/viewSpend.html",context)

    else:
        return redirect(reverse("login"))

def accountSettings(request):

    if request.user.is_authenticated:
        if request.method=="POST":
            option=request.POST['option']
            if option=="deleteme":

                username=(request.user.username)
                user=User.objects.filter(username=username)
                typed=request.POST['usertyped']
                print(typed)
                if typed==username:

                    logout(request)
                    user.delete()
                    context={"showguest":True,"showmsg":"Your account has been Deleted Succesfully..."}
                    return render(request,"tracker/home.html",context)

                else:
                    deletemsg="Error! Incorrect Username..."
                    context={"deletemsg":deletemsg,"show":True}
                    return render(request,"tracker/settings.html",context)

        else:
            context={"show":False}
            return render(request,"tracker/settings.html",context)

    else:
        context={"showguest":False,"showmsg":""}
        return render(request,"tracker/home.html")
