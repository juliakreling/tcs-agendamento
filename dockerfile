# Use an official Python runtime as a parent image
FROM python:3.8 as python-stage

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

RUN chmod +x start.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start a new stage from Node.js image
FROM node:16 as node-stage

WORKDIR /app

# Copy over the python stage
COPY --from=python-stage /app /app

# Install node modules
RUN npm install

# Make ports available to the world outside this container
EXPOSE 5000
EXPOSE 5001
EXPOSE 5002
EXPOSE 5003
EXPOSE 5004

# Run scripts
CMD ["./start.sh"]