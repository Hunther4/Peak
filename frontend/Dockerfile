FROM node:22-slim

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

# Copy frontend code
COPY . .

EXPOSE 5173

# Vite dev server with hot reload
CMD ["pnpm", "exec", "vite", "--host", "0.0.0.0"]
