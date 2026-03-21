from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, PredictionSerializer, MyTokenObtainPairSerializer
from .models import Prediction
import requests

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PredictView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        hf_api_url = "https://adharshpb-skin-lesion-model.hf.space/predict/"
        
        try:
            files = {'file': (image_file.name, image_file.read(), image_file.content_type)}
            response = requests.post(hf_api_url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                # Assuming HF space returns {"predicted_class": "Melanoma", "confidence": 94.23}
                predicted_class = result.get('predicted_class')
                confidence = result.get('confidence')
                
                # Convert image to base64
                image_file.seek(0)
                image_data = image_file.read()
                import base64
                base64_encoded = base64.b64encode(image_data).decode('utf-8')
                image_mime_type = image_file.content_type
                base64_string = f"data:{image_mime_type};base64,{base64_encoded}"
                
                prediction = Prediction.objects.create(
                    user=request.user,
                    image=base64_string,
                    predicted_class=predicted_class,
                    confidence=confidence
                )
                
                serializer = PredictionSerializer(prediction)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Prediction API failed'}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class HistoryDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            prediction = Prediction.objects.get(pk=pk, user=request.user)
            prediction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Prediction.DoesNotExist:
            return Response({'error': 'Prediction not found'}, status=status.HTTP_404_NOT_FOUND)
