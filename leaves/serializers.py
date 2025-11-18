from rest_framework import serializers
from .models import Leave
from accounts.models import User


class LeaveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Leave
        fields = '__all__'
        read_only_fields = ('applied_at', 'updated_at', 'status', 'admin_comment')

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError("End date cannot be before start date.")
        return data


class LeaveActionSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=True, required=False)
    