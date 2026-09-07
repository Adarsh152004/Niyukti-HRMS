import React, { useEffect, useRef, useState } from 'react';
import { Clock } from 'lucide-react';

export interface WorkflowNode3D {
  id: string;
  label: string;
  subtitle?: string;
  type: 'input' | 'agent' | 'tool' | 'database' | 'approval' | 'output';
  status: 'completed' | 'active' | 'waiting' | 'failed' | 'skipped' | 'upcoming';
  execution_time_ms?: number;
  position_3d?: { x: number; y: number; z: number };
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  logs?: string[];
}

export interface WorkflowEdge3D {
  source: string;
  target: string;
  label?: string;
  status?: 'completed' | 'active' | 'pending' | 'failed';
}

export interface Workflow3DData {
  query_id: string;
  query: string;
  initiator: string;
  channel: string;
  timestamp: string;
  status: string;
  duration_ms: number;
  nodes: WorkflowNode3D[];
  edges?: WorkflowEdge3D[];
}

interface Orchestration3DCanvasProps {
  workflow: Workflow3DData;
  onNodeSelect?: (node: WorkflowNode3D) => void;
}

export const Orchestration3DCanvas: React.FC<Orchestration3DCanvasProps> = ({ workflow, onNodeSelect }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Normalize nodes and generate default 3D positions if not provided
  const rawNodes = workflow?.nodes || [];
  const normalizedNodes: WorkflowNode3D[] = rawNodes.map((n, i) => {
    const defaultX = (i - (rawNodes.length - 1) / 2) * 140;
    const defaultY = Math.sin(i * 0.8) * 30;
    const defaultZ = (i % 2 === 0 ? 0 : 20);
    return {
      ...n,
      position_3d: n.position_3d || { x: defaultX, y: defaultY, z: defaultZ },
      status: n.status || 'completed'
    };
  });

  const rawEdges = workflow?.edges || [];
  const normalizedEdges: WorkflowEdge3D[] = rawEdges.length > 0 ? rawEdges : normalizedNodes.slice(0, -1).map((n, i) => ({
    source: n.id,
    target: normalizedNodes[i + 1]?.id || '',
    label: 'Next Step',
    status: 'completed'
  }));

  const [selectedNode, setSelectedNode] = useState<WorkflowNode3D | null>(normalizedNodes[0] || null);

  // 3D Spatial Camera State
  const [rotX, setRotX] = useState(0.25);
  const [rotY, setRotY] = useState(-0.35);
  const [zoom, setZoom] = useState(1.0);
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);

  const nodePositionsRef = useRef<Map<string, { x: number; y: number; z: number }>>(new Map());

  useEffect(() => {
    const map = new Map<string, { x: number; y: number; z: number }>();
    normalizedNodes.forEach((node) => {
      map.set(node.id, { ...(node.position_3d || { x: 0, y: 0, z: 0 }) });
    });
    nodePositionsRef.current = map;
  }, [workflow]);

  // Color mapping
  const getNodeColor = (type: string, status: string) => {
    if (status === 'active') return '#06b6d4'; // Cyan
    if (status === 'completed') {
      switch (type) {
        case 'input': return '#38bdf8'; // Sky
        case 'agent': return '#6366f1'; // Indigo
        case 'tool': return '#10b981'; // Emerald
        case 'database': return '#8b5cf6'; // Purple
        case 'approval': return '#f59e0b'; // Amber
        case 'output': return '#f43f5e'; // Rose
        default: return '#94a3b8';
      }
    }
    return '#475569'; // Slate muted
  };

  // Main 3D Canvas Projection & Animation Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let particleOffset = 0;

    const render = () => {
      // Handle High DPI scaling
      const width = canvas.parentElement?.clientWidth || 800;
      const height = 480;
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }

      ctx.clearRect(0, 0, width, height);

      // Dark Neon Matrix Grid Background
      ctx.fillStyle = '#020617';
      ctx.fillRect(0, 0, width, height);

      // 3D Isometric Ground Grid
      ctx.strokeStyle = 'rgba(30, 41, 59, 0.4)';
      ctx.lineWidth = 1;
      const gridSize = 40;
      const cx = width / 2;
      const cy = height / 2;

      for (let gx = -300; gx <= 300; gx += gridSize) {
        const p1 = project3D(gx, 100, -300, rotX, rotY, zoom, cx, cy);
        const p2 = project3D(gx, 100, 300, rotX, rotY, zoom, cx, cy);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
      for (let gz = -300; gz <= 300; gz += gridSize) {
        const p1 = project3D(-300, 100, gz, rotX, rotY, zoom, cx, cy);
        const p2 = project3D(300, 100, gz, rotX, rotY, zoom, cx, cy);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }

      // Project Nodes
      const projectedNodes: Array<{
        node: WorkflowNode3D;
        x: number;
        y: number;
        z: number;
        scale: number;
        color: string;
      }> = [];

      normalizedNodes.forEach((node) => {
        const pos = nodePositionsRef.current.get(node.id) || node.position_3d || { x: 0, y: 0, z: 0 };
        const p = project3D(pos.x, pos.y, pos.z, rotX, rotY, zoom, cx, cy);
        const color = getNodeColor(node.type, node.status);
        projectedNodes.push({ node, x: p.x, y: p.y, z: p.z, scale: p.scale, color });
      });

      // Sort by Z for Depth
      projectedNodes.sort((a, b) => b.z - a.z);

      // Render Edges & Particle Beams
      particleOffset += 0.015;
      normalizedEdges.forEach((edge) => {
        const sourceP = projectedNodes.find((n) => n.node.id === edge.source);
        const targetP = projectedNodes.find((n) => n.node.id === edge.target);

        if (sourceP && targetP) {
          // Line Glow
          ctx.strokeStyle = edge.status === 'active' ? '#06b6d4' : 'rgba(99, 102, 241, 0.4)';
          ctx.lineWidth = edge.status === 'active' ? 3 : 1.5;
          ctx.beginPath();
          ctx.moveTo(sourceP.x, sourceP.y);
          ctx.lineTo(targetP.x, targetP.y);
          ctx.stroke();

          // Animated Signal Particle along edge
          const t = (particleOffset % 1);
          const px = sourceP.x + (targetP.x - sourceP.x) * t;
          const py = sourceP.y + (targetP.y - sourceP.y) * t;

          ctx.fillStyle = '#38bdf8';
          ctx.shadowColor = '#38bdf8';
          ctx.shadowBlur = 10;
          ctx.beginPath();
          ctx.arc(px, py, 3.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Render 3D Cubes / Node Spheres
      projectedNodes.forEach(({ node, x, y, scale, color }) => {
        const isSelected = selectedNode?.id === node.id;
        const radius = Math.max(16 * scale, 10);

        // Ground Shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.beginPath();
        ctx.ellipse(x, y + radius + 15 * scale, radius * 1.2, radius * 0.4, 0, 0, Math.PI * 2);
        ctx.fill();

        // Node Glow Halo
        ctx.fillStyle = isSelected ? 'rgba(99, 102, 241, 0.3)' : `${color}22`;
        ctx.beginPath();
        ctx.arc(x, y, radius * 1.6, 0, Math.PI * 2);
        ctx.fill();

        // Node Sphere Base
        const grad = ctx.createRadialGradient(
          x - radius * 0.3,
          y - radius * 0.3,
          radius * 0.1,
          x,
          y,
          radius
        );
        grad.addColorStop(0, '#ffffff');
        grad.addColorStop(0.3, color);
        grad.addColorStop(1, '#0f172a');

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();

        // Active Pulsing Ring
        if (node.status === 'active') {
          ctx.strokeStyle = '#06b6d4';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(x, y, radius * (1.2 + 0.2 * Math.sin(Date.now() / 200)), 0, Math.PI * 2);
          ctx.stroke();
        }

        // Selected Border
        if (isSelected) {
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.arc(x, y, radius * 1.2, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Text Billboard Label
        ctx.font = `bold ${Math.max(11 * scale, 9)}px sans-serif`;
        ctx.fillStyle = '#f8fafc';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, x, y - radius - 8 * scale);

        // Subtitle / Type
        ctx.font = `${Math.max(9 * scale, 7.5)}px sans-serif`;
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(node.subtitle || node.type.toUpperCase(), x, y - radius - 20 * scale);
      });

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [normalizedNodes, normalizedEdges, rotX, rotY, zoom, selectedNode]);

  // Mouse Interaction (Orbit Controls)
  const isDragging = useRef(false);
  const lastMousePos = useRef({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    isDragging.current = true;
    lastMousePos.current = { x: e.clientX, y: e.clientY };

    // Check if clicked a node
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    normalizedNodes.forEach((node) => {
      const pos = nodePositionsRef.current.get(node.id) || node.position_3d || { x: 0, y: 0, z: 0 };
      const p = project3D(pos.x, pos.y, pos.z, rotX, rotY, zoom, cx, cy);
      const dist = Math.hypot(p.x - mouseX, p.y - mouseY);
      if (dist < 24) {
        setSelectedNode(node);
        if (onNodeSelect) onNodeSelect(node);
      }
    });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging.current) return;
    const dx = e.clientX - lastMousePos.current.x;
    const dy = e.clientY - lastMousePos.current.y;

    setRotY((prev) => prev + dx * 0.006);
    setRotX((prev) => Math.max(-1.2, Math.min(1.2, prev + dy * 0.006)));

    lastMousePos.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    setZoom((prev) => Math.max(0.4, Math.min(2.2, prev - e.deltaY * 0.001)));
  };

  return (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl">
      {/* 3D Canvas */}
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        className="w-full h-[480px] cursor-grab active:cursor-grabbing block"
      />

      {/* Floating Canvas UI Overlay */}
      <div className="absolute top-4 left-4 flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 text-xs text-slate-300 pointer-events-none">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
        <span className="font-semibold text-white">Spatial Multi-Agent DAG</span>
        <span className="text-slate-500">•</span>
        <span className="text-2xs text-slate-400">Drag to Orbit, Scroll to Zoom</span>
      </div>

      {/* Reset Camera Button */}
      <div className="absolute top-4 right-4 flex items-center gap-2">
        <button
          onClick={() => {
            setRotX(0.25);
            setRotY(-0.35);
            setZoom(1.0);
          }}
          className="px-2.5 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-3xs font-semibold text-slate-300 border border-slate-700/60 transition shadow-sm"
        >
          Reset Camera
        </button>
      </div>

      {/* Selected Node Details Floating Glass Card */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 right-4 sm:right-auto sm:max-w-md bg-slate-900/90 backdrop-blur-md p-4 rounded-xl border border-slate-700/70 shadow-2xl space-y-2">
          <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: getNodeColor(selectedNode.type, selectedNode.status) }} />
              <h4 className="text-xs font-bold text-white">{selectedNode.label}</h4>
            </div>
            <span className="px-2 py-0.5 rounded text-3xs font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
              {selectedNode.type}
            </span>
          </div>

          <p className="text-2xs text-slate-300">{selectedNode.subtitle || 'Step execution detail'}</p>

          {selectedNode.execution_time_ms !== undefined && (
            <div className="flex items-center gap-2 text-3xs text-slate-400 pt-1">
              <Clock className="w-3 h-3 text-cyan-400" />
              <span>Execution Time: <strong className="text-cyan-300">{selectedNode.execution_time_ms} ms</strong></span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// 3D Math Helper Function: Projects 3D (X, Y, Z) point into 2D Screen coordinates with Rotation & Zoom
function project3D(
  x: number,
  y: number,
  z: number,
  rotX: number,
  rotY: number,
  zoom: number,
  cx: number,
  cy: number
): { x: number; y: number; z: number; scale: number } {
  // Rotate around Y axis
  const cosY = Math.cos(rotY);
  const sinY = Math.sin(rotY);
  const x1 = x * cosY + z * sinY;
  const z1 = -x * sinY + z * cosY;

  // Rotate around X axis
  const cosX = Math.cos(rotX);
  const sinX = Math.sin(rotX);
  const y2 = y * cosX - z1 * sinX;
  const z2 = y * sinX + z1 * cosX;

  // Perspective Projection
  const fov = 400;
  const distance = 400;
  const scale = (fov / (distance + z2)) * zoom;

  return {
    x: cx + x1 * scale,
    y: cy + y2 * scale,
    z: z2,
    scale
  };
}
