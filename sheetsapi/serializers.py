from rest_framework import serializers
from .models import UserForm  # Assuming you have a model for this

class UserFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserForm
        fields = [
            'team_name', 
            'team_leader', 
            'leader_contact', 
            'email', 
            'college_name', 
            'member1', 
            'member1_contact', 
            'member2', 
            'member2_contact', 
            'member3', 
            'member3_contact', 
            'member4', 
            'member4_contact'
            ]
