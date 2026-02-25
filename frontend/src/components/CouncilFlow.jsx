import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { Streamdown } from 'streamdown';
import 'streamdown/styles.css';
import {
    ReactFlow,
    Controls,
    Background,
    applyNodeChanges,
    applyEdgeChanges,
    addEdge,
    Handle,
    Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const CustomNode = ({ data, id }) => {
    return (
        <div className="card" style={{ padding: '1rem', minWidth: '150px', maxWidth: '300px' }}>
            {id !== 'user-prompt' && (
                <Handle type="target" position={Position.Left} style={{ background: '#555' }} />
            )}
            <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                <Streamdown>{data.label || ""}</Streamdown>
            </div>
            {id !== 'chairman' && (
                <Handle type="source" position={Position.Right} style={{ background: '#555' }} />
            )}
        </div>
    );
};

const nodeTypes = {
    custom: CustomNode,
};

const initialNodes = [
    {
        id: 'user-prompt',
        data: { label: 'User Prompt' },
        position: { x: 50, y: 250 },
        type: 'custom',
        sourcePosition: 'right',
    },
    {
        id: 'member-1',
        data: { label: 'Member 1' },
        position: { x: 350, y: 150 },
        type: 'custom',
        targetPosition: 'left',
        sourcePosition: 'right',
    },
    {
        id: 'member-2',
        data: { label: 'Member 2' },
        position: { x: 350, y: 250 },
        type: 'custom',
        targetPosition: 'left',
        sourcePosition: 'right',
    },
    {
        id: 'member-3',
        data: { label: 'Member 3' },
        position: { x: 350, y: 350 },
        type: 'custom',
        targetPosition: 'left',
        sourcePosition: 'right',
    },
    {
        id: 'chairman',
        data: { label: 'Chairman' },
        position: { x: 700, y: 250 },
        type: 'custom',
        targetPosition: 'left',
    },
];

const initialEdges = [
    { id: 'u-m1', source: 'user-prompt', target: 'member-1' },
    { id: 'u-m2', source: 'user-prompt', target: 'member-2' },
    { id: 'u-m3', source: 'user-prompt', target: 'member-3' },
    { id: 'm1-c', source: 'member-1', target: 'chairman' },
    { id: 'm2-c', source: 'member-2', target: 'chairman' },
    { id: 'm3-c', source: 'member-3', target: 'chairman' },
];

export default function CouncilFlow() {
    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);
    const [prompt, setPrompt] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        axios.get('/api/models').then(res => {
            const memModels = res.data.member_models;
            const chairModels = res.data.chairman_models;
            setNodes(nds => nds.map(n => {
                if (n.id === 'member-1' && memModels[0]) return { ...n, data: { ...n.data, label: memModels[0] } };
                if (n.id === 'member-2' && memModels[1]) return { ...n, data: { ...n.data, label: memModels[1] } };
                if (n.id === 'member-3' && memModels[2]) return { ...n, data: { ...n.data, label: memModels[2] } };
                if (n.id === 'chairman' && chairModels[0]) return { ...n, data: { ...n.data, label: chairModels[0] } };
                return n;
            }));
        }).catch(err => console.error("Could not fetch models", err));
    }, []);

    const onNodesChange = useCallback(
        (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
        []
    );

    const onEdgesChange = useCallback(
        (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
        []
    );

    const onConnect = useCallback(
        (params) => setEdges((eds) => addEdge(params, eds)),
        []
    );

    const handleRunCouncil = async (e) => {
        e.preventDefault();
        const currPrompt = prompt;
        if (!currPrompt.trim()) return;

        setIsLoading(true);
        setPrompt("");

        // turn nodes to thinking and dump input box contnet to user-prompt node
        setNodes((nds) => nds.map((node) => {
            if (node.id === 'user-prompt') return { ...node, data: { ...node.data, label: currPrompt } };
            if (node.id.startsWith('member-') || node.id === 'chairman') {
                return { ...node, data: { ...node.data, label: 'Thinking...' } };
            }
            return node;
        }));

        try {
            const res = await axios.post('/api/chat', { message: currPrompt });
            console.log("Response:", res.data);
            const { response, intermediate } = res.data;

            setNodes((nds) => nds.map((node) => {
                if (node.id === 'member-1') return { ...node, data: { ...node.data, label: intermediate && intermediate[0] ? intermediate[0] : 'No response' } };
                if (node.id === 'member-2') return { ...node, data: { ...node.data, label: intermediate && intermediate[1] ? intermediate[1] : 'No response' } };
                if (node.id === 'member-3') return { ...node, data: { ...node.data, label: intermediate && intermediate[2] ? intermediate[2] : 'No response' } };
                if (node.id === 'chairman') return { ...node, data: { ...node.data, label: response || 'No response' } };
                return node;
            }));

        } catch (error) {
            console.error("Error calling council API", error);
            setNodes((nds) => nds.map((node) => {
                if (node.id.startsWith('member-') || node.id === 'chairman') {
                    return { ...node, data: { ...node.data, label: 'Error occurred' } };
                }
                return node;
            }));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ width: '100vw', height: '100vh', background: '#f8f9fa', position: 'relative' }}>

            {/* Floating UI Panel */}
            <div className="floating-panel">
                <form onSubmit={handleRunCouncil} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleRunCouncil(e);
                            }
                        }}
                        placeholder="Ask the council... (Press Enter to send, Shift+Enter for new line)"
                        disabled={isLoading}
                        style={{ width: '400px', margin: 0, minHeight: '40px' }}
                    />
                    <button type="submit" disabled={isLoading}>
                        {isLoading ? 'Running...' : 'Run Council'}
                    </button>
                </form>
            </div>

            <ReactFlow
                nodes={nodes}
                onNodesChange={onNodesChange}
                edges={edges}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
            >
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
}
