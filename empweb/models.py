from django.db import models
from django.contrib.auth.models import User


class Departmentmaster(models.Model):
    department_id=models.AutoField(primary_key=True)
    department_name=models.CharField(max_length=100)
    description=models.CharField(max_length=100)
    created_by_user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    created_at_date=models.DateField(auto_now_add=True,null=True,blank=True)
    updated_by_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="updated",null=True)
    updated_by_date=models.DateField(null=True)
    


    def __str__(self):
        return self.department_name


class SubDepartmentmaster(models.Model):
    sub_department_id=models.AutoField(primary_key=True)
    department_id=models.ForeignKey(Departmentmaster, on_delete=models.CASCADE)
    sub_department_name=models.CharField(max_length=110)
    description=models.CharField(max_length=100)
    created_by_user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    created_at_date=models.DateField(auto_now_add=True)
    updated_by_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="update",null=True)
    updated_by_date=models.DateField(null=True)

    def __str__(self):
        return self.sub_department_name
    
class EmployeeMaster(models.Model):
    emp_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=250)
    join_date=models.DateField()
    department=models.ForeignKey(Departmentmaster,on_delete=models.CASCADE)
    sub_department=models.ForeignKey(SubDepartmentmaster,on_delete=models.CASCADE)
    created_by_user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    created_at_date=models.DateField(auto_now_add=True)
    updated_at=models.DateField(null=True)
    updated_by_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="name",null=True)
    emp_no=models.IntegerField(null=True)
    address=models.CharField(max_length=250,null=True)
    emp_start_date=models.DateField(null=True)
    emp_end_date=models.DateField(null=True)
    
    
    def __str__(self):
        return self.name
    
class Subjects(models.Model):
    sub_id=models.AutoField(primary_key=True)
    sub_name=models.CharField(max_length=250)
    description=models.CharField(max_length=250)
    department_id=models.ForeignKey(Departmentmaster, on_delete=models.CASCADE)


    def __str__(self):
        return self.sub_name
