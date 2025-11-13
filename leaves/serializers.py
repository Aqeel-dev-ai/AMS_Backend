# leaves/serializers.py
from rest_framework import serializers
from .models import Leave

class LeaveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id', 'user', 'username',
            'leave_type', 'start_date', 'end_date', 'reason',
            'status', 'admin_comment', 'applied_at', 'updated_at'
        ]
        read_only_fields = ('applied_at', 'updated_at', 'user', 'status', 'admin_comment')

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError("End date cannot be before start date.")
        return data
