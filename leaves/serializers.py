from rest_framework import serializers
from .models import Leave
from accounts.models import User


class LeaveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, write_only=True)
    applied_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, write_only=True, allow_null=True)
    
    # Target user (who the leave is for)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id', 'user', 'user_id', 'user_name', 'applied_by',
            'leave_type', 'start_date', 'end_date', 'reason', 
            'status', 'admin_comment', 'applied_at', 'updated_at'
        ]
        read_only_fields = ('id', 'applied_at', 'updated_at', 'user_id', 'user_name')

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError("End date cannot be before start date.")
        return data


class LeaveActionSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=True, required=False)
    