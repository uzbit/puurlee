# Use an official Python runtime as a parent image
FROM python:3.10-slim

# # Install Tesseract and any libraries you need
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     tesseract-ocr \
#     libtesseract-dev \
#     libleptonica-dev \
#     pkg-config \
#     poppler-utils \
#     && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy requirements and install them (if you have dependencies)

# Copy in your function code
COPY clear_user_data/ /app
COPY utils /app/utils
COPY options.ini /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# 
# If you have a specific entry point function, specify it below.
# For example, if your main function is "ocr_function" in "main.py",
# then set FUNCTION_TARGET=ocr_function.
#
# Cloud Functions by default will listen on port 8080, 
# which the Functions Framework respects.
#
ENV FUNCTION_TARGET=main
ENV PORT=8080
ENV PYTHONPATH=/app

# Expose port 8080 for Cloud Functions
EXPOSE 8080

# Finally, start the Functions Framework
CMD ["functions-framework", "--target=main", "--port=8080"]
