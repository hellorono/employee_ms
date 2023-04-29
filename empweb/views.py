from django.shortcuts import render

from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.utils import timezone
from empweb import models
from django.views.generic import CreateView,FormView,ListView,UpdateView,TemplateView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from datetime import datetime
from .forms import *
from empweb.models import Departmentmaster,SubDepartmentmaster,EmployeeMaster,Subjects
from django.core.paginator import Paginator
import xlwt
from django.contrib.auth.models import User
from django.http import HttpResponse,HttpResponseNotAllowed
from django.contrib import messages
from django.forms import modelformset_factory,inlineformset_factory



def signin_required(fn):
    def wrapper(request,*args,**kw):
        if not request.user.is_authenticated:
            return redirect("signin")
        else:
            return fn(request,*args,**kw)
    return wrapper

decs=[signin_required,never_cache]


class SignUpView(CreateView):
    template_name="register.html"
    form_class=UserRegistrationForm
    success_url=reverse_lazy("index")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials')
            
    return render(request, 'login.html')
            

@method_decorator(decs,name="dispatch")
class IndexView(ListView,LoginRequiredMixin):
    template_name="index.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def index_view(request):
    
        if 'user_id' in request.session:
            return render(request, 'index.html')
        else:
        
            return redirect('login')
    
@method_decorator(decs,name="dispatch")
class DeptMasterView(ListView):
    template_name='departmentmaster.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
@method_decorator(decs,name="dispatch")
class DeptMasterCreateView(TemplateView):
    
    def get(self,request,*args,**kw):
        form=DepartmentMasterForm()
        formset=SubjectAddFormSet(queryset=Subjects.objects.none())
        context={"form":form,"formset":formset}
        return render (request,"add_deptmaster.html",context)
    
    def post(self,request,*args,**kw):
        form=DepartmentMasterForm(request.POST)
        formset=SubjectAddFormSet(request.POST,request.FILES)
        context={"form":form,"formset":formset}


        if form.is_valid() and formset.is_valid():
            instance=form.save(commit=False)
            instance.created_by_user=request.user
            instance.save()
    
       
            for form in formset:
                sub = form.save(commit=False)
                sub.department_id = instance
                sub.save()

            return redirect("list-deptmaster")
        else:
            return render(request,"add_deptmaster.html",context)
        

@method_decorator(decs,name="dispatch")
class DeptMasterListView(ListView):
    template_name="list_deptmaster.html"
    model=Departmentmaster
    
    def get(self,request,*args,**kw):
        data=Departmentmaster.objects.all()
       
        context={'data':data}
        return render(request,'list_deptmaster.html',context)



@method_decorator(decs,name="dispatch")
class UpdateDepartmentMaster(TemplateView):

    def get(self,request,*args,**kw):
        obj=Departmentmaster.objects.get(department_id=kw["pk"])
        form=DepartmentMasterForm(instance=obj)
        formset=SubjectEditFormSet(queryset=Subjects.objects.filter(department_id=obj))
        context={"form":form,"formset":formset,"obj":obj}
        return render (request,"updatedepmaster.html",context)
    
    def post(self,request,*args,**kw):
        obj=Departmentmaster.objects.get(department_id=kw["pk"])
        form=DepartmentMasterForm(data=request.POST,instance=obj)
        formset=SubjectEditFormSet(data=request.POST,queryset=Subjects.objects.filter(department_id=obj))
        context={"form":form,"formset":formset,"obj":obj}
        
        if form.is_valid() and formset.is_valid():
            print(formset.cleaned_data)
            instance=form.save(commit=False)
            print(instance)
            instance.updated_by_user=request.user
            instance.updated_by_date=datetime.now()
            instance.save()

            for form in formset:
                sub=form.save(commit=False)
                sub.department_id=instance
                sub.save()

            return redirect("list-deptmaster")
        else:
            
            print(formset.errors)
            return render(request,"updatedepmaster.html",context)
        


def departmentmaster_delete(request,pk):
    if request.method=="GET":
        id=pk
        Departmentmaster.objects.get(department_id=id).delete()
        return redirect("list-deptmaster")  

@method_decorator(decs,name="dispatch")
class SubDeptMasterView(ListView):
    template_name='subdeptmaster.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

@method_decorator(decs,name="dispatch")
class SubdeptCreateView(TemplateView):
    def get(self,request,*args,**kw):
        form=SubdepartmentMasterForm()
        context={"form":form}
        return render (request,"add_sub.html",context)

    def post(self,request,*args,**kw):
        form=SubdepartmentMasterForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.created_by_user=request.user
            instance.save()

            return redirect("list_sub")
        else:
            return render(request,"add_sub",{"form":form})

@method_decorator(decs,name="dispatch")
class SubdeptListView(ListView):
    template_name="list_sub.html"
    model=SubDepartmentmaster

    def get(self,request,*args,**kw):
        data=SubDepartmentmaster.objects.all()
        paginator=Paginator(data,3)
        page_number=request.GET.get('page')
        data=paginator.get_page(page_number)
        context={"data":data}
        return render(request,'list_sub.html',context)

@method_decorator(decs,name="dispatch")
class UpdateSubDepartmentMasterView(TemplateView):
    def get(self,request,*args,**kw):
        obj=SubDepartmentmaster.objects.get(sub_department_id=kw["pk"])
        form=SubdepartmentMasterForm(instance=obj)
        context={"form":form}
        return render (request,"update_sub.html",context)
    
    def post(self,request,*args,**kw):
        obj=SubDepartmentmaster.objects.get(sub_department_id=kw["pk"])
        form=SubdepartmentMasterForm(instance=obj,data=request.POST)
        if form.is_valid():
            
            instance=form.save(commit=False)
            instance.updated_by_user=request.user
            instance.updated_by_date=datetime.now()
            instance.save() 

            return redirect("list_sub")
        else:
            return render(request,"update_sub.html",{"form":form})
            
def delete_sub(request,pk):
    if request.method=="GET":
        id=pk
        SubDepartmentmaster.objects.get(sub_department_id=id).delete()
        return redirect("list_sub")

@method_decorator(decs,name="dispatch")    
class EmployeeMasterView(ListView):
    template_name="employeemaster.html"
    def get(self,request,*args,**kw):
        return render(request,self.template_name)

@method_decorator(decs,name="dispatch")
class EmployeeCreateView(TemplateView,CreateView):
    def get(self,request,*args,**kw):
        form=EmpolyeeForm()
        context={"form":form}
        return render(request,"emp_add.html",context)
        
    def post(self,request,*args,**kw):
        form=EmpolyeeForm(request.POST)
        print(request.POST)
        print(request.POST.get('sub_department'),":::subdept")
        if form.is_valid():
            instance=form.save(commit=False)
            instance.created_by_user=request.user
            instance.save()
            
            
            return redirect("emp_list")
        else:
            
            return render(request,"emp_add.html",{"form":form})
            


@method_decorator(decs,name="dispatch")
class EmployeeListView(ListView):

    def get(self,request,*args,**kw):
        data=EmployeeMaster.objects.all()
        context={"data":data}
        return render(request,"emp_list.html",context)
    
    
def employee_list(request):
    employees = EmployeeMaster.objects.all()
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    
    if from_date and to_date:
        from_date = timezone.datetime.strptime(from_date, '%Y-%m-%d')
        to_date = timezone.datetime.strptime(to_date, '%Y-%m-%d')
        employees = employees.filter(join_date__range=(from_date, to_date))
    
    paginator = Paginator(employees, 3)
    page_number = request.GET.get('page')
    employees = paginator.get_page(page_number)
    
    context = {'employees': employees}
    return render(request, 'emp_list.html', context)

@method_decorator(decs,name="dispatch")
class UpdateEmployeeListView(TemplateView):
    def get(self,request,*args,**kw):
        obj=EmployeeMaster.objects.get(emp_id=kw["pk"])
        form=EmpolyeeForm(instance=obj)
        context={"form":form}
        return render(request,"emp_update.html",context)

    def post(self,request,*args,**kw):
        obj=EmployeeMaster.objects.get(emp_id=kw["pk"])
        form=EmpolyeeForm(instance=obj,data=request.POST)
        
        if form.is_valid():
            instance=form.save(commit=False)
            instance.updated_by_user=request.user
            instance.updated_by_date=datetime.now()
            instance.save()
            return redirect("emp_list")
        else:
            return render(request,"emp_update.html",{"form":form})
        
@method_decorator(decs,name="dispatch")
class EmployeeDetailView(TemplateView):
    def get(self,request,*args,**kw):
        data=EmployeeMaster.objects.get(emp_id=kw["pk"])
        context={"data":data}
        return render(request,"emp_detail.html",context)
        
def delete_employee(request,pk):
    if request.method=="GET":
        id=pk
        EmployeeMaster.objects.get(emp_id=id).delete()
        return redirect("emp_list")
    
def sign_out_view(request,*args,**kw):
    logout(request)
    return redirect("signin")

def load_employee(request):
    department_id=request.GET.get('department_id')
    sub=SubDepartmentmaster.objects.filter(department_id=department_id)
    new = [(c.sub_department_id, c.sub_department_name) for c in sub]
    data={"sub":new}
    return JsonResponse(data)


def export_excel(request):
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment;filename=Employeeslist'+\
        str(datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Employee')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True


    columns=['emp_id',"name",'join_date','department','sub_department','created_by_user','created_at_date','updated_at','updated_by_user','emp_no','address','emp_start_date','emp_end_date']
    
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style=xlwt.XFStyle()
    rows=EmployeeMaster.objects.all().values_list('emp_id',"name",'join_date','department','sub_department','created_by_user','created_at_date','updated_at','updated_by_user','emp_no','address','emp_start_date','emp_end_date')

    for row in rows:
        row_num+=1

        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


