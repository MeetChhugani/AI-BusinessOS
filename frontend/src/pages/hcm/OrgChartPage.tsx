import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';
import { motion } from 'framer-motion';

interface OrgNode {
  id: string;
  pid: string | null;
  name: string;
  title: string;
  department: string;
  avatar: string;
  status: string;
}

export const OrgChartPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [nodes, setNodes] = useState<OrgNode[]>([]);
  const [zoom, setZoom] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const fetchChart = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/organization/chart', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setNodes(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchChart();
    }
  }, [accessToken]);

  // Construct tree nodes hierarchy
  const buildTree = (list: OrgNode[]) => {
    const map: { [key: string]: any } = {};
    const tree: any[] = [];
    
    list.forEach(node => {
      map[node.id] = { ...node, children: [] };
    });
    
    list.forEach(node => {
      if (node.pid && map[node.pid]) {
        map[node.pid].children.push(map[node.id]);
      } else {
        tree.push(map[node.id]);
      }
    });
    
    return tree;
  };

  const TreeNode: React.FC<{ node: any }> = ({ node }) => (
    <div className="flex flex-col items-center">
      {/* Node Display Card */}
      <motion.div 
        whileHover={{ scale: 1.02 }}
        className="glass-card rounded-xl p-4 border border-neutral-800 text-center w-52 flex flex-col items-center shadow-lg relative glow-border bg-card/85"
      >
        <img src={node.avatar} alt="Avatar" className="w-10 h-10 rounded-full border border-border mb-2.5 bg-neutral-900" />
        <h4 className="text-xs font-bold text-white leading-tight">{node.name}</h4>
        <span className="text-[10px] text-blue-400 font-semibold block mt-0.5">{node.title}</span>
        <span className="text-[9px] text-muted-foreground uppercase tracking-wider block mt-1">{node.department}</span>
      </motion.div>

      {/* Children lines & layouts */}
      {node.children && node.children.length > 0 && (
        <div className="flex flex-col items-center">
          {/* Vertical Link connector Line down */}
          <div className="w-px h-6 bg-neutral-800" />
          
          <div className="flex space-x-8 relative">
            {node.children.map((child: any, idx: number) => (
              <div key={child.id} className="flex flex-col items-center relative">
                {/* Horizontal link connectors */}
                {node.children.length > 1 && (
                  <div className="absolute top-0 w-full h-px bg-neutral-800" 
                    style={{
                      left: idx === 0 ? '50%' : '-50%',
                      width: idx === 0 || idx === node.children.length - 1 ? '50%' : '100%'
                    }}
                  />
                )}
                {/* Vertical child link down */}
                <div className="w-px h-6 bg-neutral-800" />
                <TreeNode node={child} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const tree = buildTree(nodes);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Organization Structure
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Visualize reporting hierarchies, managers, and operational structure.
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-secondary border border-border p-1 rounded-lg">
          <button onClick={() => setZoom(z => Math.max(0.5, z - 0.1))} className="p-1.5 text-muted-foreground hover:text-white rounded hover:bg-neutral-800 transition" title="Zoom Out">
            <ZoomOut size={16} />
          </button>
          <span className="text-xs text-white font-mono px-2">{Math.round(zoom * 100)}%</span>
          <button onClick={() => setZoom(z => Math.min(1.5, z + 0.1))} className="p-1.5 text-muted-foreground hover:text-white rounded hover:bg-neutral-800 transition" title="Zoom In">
            <ZoomIn size={16} />
          </button>
          <button onClick={() => setZoom(1)} className="p-1.5 text-muted-foreground hover:text-white rounded hover:bg-neutral-800 transition" title="Reset">
            <Maximize size={16} />
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="glass-card rounded-2xl border border-neutral-800 p-12 min-h-[500px] overflow-auto flex items-start justify-center relative bg-black/20">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : tree.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            No organization hierarchy nodes seeded yet.
          </div>
        ) : (
          <div 
            className="origin-top transition-transform duration-200"
            style={{ transform: `scale(${zoom})` }}
          >
            {tree.map(rootNode => (
              <TreeNode key={rootNode.id} node={rootNode} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
