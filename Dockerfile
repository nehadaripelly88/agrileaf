FROM python:3.11-slim
 
WORKDIR /app
 
# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy all project files
COPY . .
 
# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
 
# Expose port
EXPOSE 7860
 
# Run the app
CMD ["python", "run.py"]