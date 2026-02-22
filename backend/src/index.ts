import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config({ path: '../.env' });

const app = express();
app.use(cors());

const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Middleware for Multi-tenant Workspace Isolation
io.use((socket, next) => {
  const workspaceId = socket.handshake.auth.workspaceId;
  if (!workspaceId) return next(new Error("Invalid Workspace"));
  (socket as any).workspaceId = workspaceId;
  next();
});

io.on('connection', (socket) => {
  const workspaceId = (socket as any).workspaceId;
  socket.join(workspaceId);
  
  console.log(`🚀 User connected to Workspace: ${workspaceId}`);

  // Presence Indicator: Broadcast "User is typing"
  socket.on('typing', (data) => {
    socket.to(workspaceId).emit('user_typing', data);
  });

  // Activity Feed: Task Updates
  socket.on('task_update', (task) => {
    io.to(workspaceId).emit('activity_log', {
      user: task.user,
      action: `moved ${task.title} to ${task.status}`,
      time: new Date()
    });
  });

  socket.on('disconnect', () => {
    console.log('❌ User disconnected');
  });
});

const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`📡 Pulse Server running on port ${PORT}`);
});