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
        read_only_fields = ('applied_at', 'updated_at', 'user')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and not request.user.is_anonymous:
            validated_data['user'] = request.user
        return super().create(validated_data)
