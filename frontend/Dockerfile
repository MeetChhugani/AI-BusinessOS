FROM node:20-alpine

WORKDIR /app

# Copy package configurations
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start the development server by default
CMD ["npm", "run", "dev", "--", "--host"]
