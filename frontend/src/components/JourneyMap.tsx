import React, { useEffect, useMemo, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  Edge,
  MarkerType,
  MiniMap,
  Node,
  Position,
  useEdgesState,
  useNodesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { getJourney, JourneyNode, JourneyResponse } from '../api';

interface ColorSet {
  bg: string;
  border: string;
  text: string;
}

const UNSCHEDULED_LABEL = 'Not Scheduled';

const semesterSortValue = (semester: string) => {
  if (semester === UNSCHEDULED_LABEL) {
    return { year: 9999, season: 99 };
  }

  const [seasonLabel, yearLabel] = semester.split(' ');
  const year = Number.parseInt(yearLabel, 10);
  const seasonMap: Record<string, number> = {
    Spring: 1,
    Summer: 2,
    Fall: 3,
    Winter: 4,
  };

  return {
    year: Number.isNaN(year) ? 9998 : year,
    season: seasonMap[seasonLabel] ?? 98,
  };
};

const buildSemesterColors = (semesters: string[]): Map<string, ColorSet> => {
  const map = new Map<string, ColorSet>();

  semesters
    .filter((semester) => semester !== UNSCHEDULED_LABEL)
    .forEach((semester, index) => {
      const hue = (index * 67) % 360;
      map.set(semester, {
        bg: `hsl(${hue} 70% 45%)`,
        border: `hsl(${hue} 65% 35%)`,
        text: '#ffffff',
      });
    });

  map.set(UNSCHEDULED_LABEL, {
    bg: '#6b7280',
    border: '#4b5563',
    text: '#ffffff',
  });

  return map;
};

const getNodeColor = (
  semester: string | null | undefined,
  completed: boolean,
  colors: Map<string, ColorSet>
): ColorSet => {
  const normalizedSemester = semester || UNSCHEDULED_LABEL;
  const base = colors.get(normalizedSemester) || colors.get(UNSCHEDULED_LABEL)!;
  const opacity = completed ? 1 : 0.6;

  const hexToRgba = (hex: string, alpha: number) => {
    const normalized = hex.replace('#', '');
    const bigint = Number.parseInt(normalized, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  if (base.bg.startsWith('#')) {
    return {
      bg: hexToRgba(base.bg, opacity),
      border: base.border,
      text: base.text,
    };
  }

  return {
    bg: base.bg.replace(')', ` / ${opacity})`).replace('hsl(', 'hsl('),
    border: base.border,
    text: base.text,
  };
};

const JourneyMap: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [semesterList, setSemesterList] = useState<string[]>([]);

  const semesterColors = useMemo(() => buildSemesterColors(semesterList), [semesterList]);

  const fetchJourney = React.useCallback(async () => {
    try {
      const response = await getJourney();
      const data: JourneyResponse = response.data;

      const semesterGroups: Record<string, JourneyNode[]> = {};
      data.nodes.forEach((course) => {
        const semester = course.semester || UNSCHEDULED_LABEL;
        if (!semesterGroups[semester]) {
          semesterGroups[semester] = [];
        }
        semesterGroups[semester].push(course);
      });

      const sortedSemesters = Object.keys(semesterGroups).sort((a, b) => {
        const av = semesterSortValue(a);
        const bv = semesterSortValue(b);

        if (av.year !== bv.year) {
          return av.year - bv.year;
        }
        return av.season - bv.season;
      });

      setSemesterList(sortedSemesters);
      const dynamicColors = buildSemesterColors(sortedSemesters);

      const flowNodes: Node[] = [];
      const columnWidth = 300;
      const rowHeight = 120;
      const startX = 50;
      const startY = 100;

      sortedSemesters.forEach((semester, semesterIndex) => {
        const courses = semesterGroups[semester];
        const x = startX + semesterIndex * columnWidth;

        flowNodes.push({
          id: `header-${semester}`,
          type: 'default',
          position: { x, y: 20 },
          data: {
            label: (
              <div
                style={{
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: '#374151',
                  textAlign: 'center',
                  padding: '8px',
                  background: '#f3f4f6',
                  borderRadius: '8px',
                  border: '2px solid #d1d5db',
                }}
              >
                {semester}
              </div>
            ),
          },
          draggable: false,
          selectable: false,
        });

        courses.forEach((course, courseIndex) => {
          const y = startY + courseIndex * rowHeight;
          const colors = getNodeColor(course.semester, course.completed, dynamicColors);

          flowNodes.push({
            id: course.id,
            type: 'default',
            position: { x, y },
            data: {
              label: (
                <div
                  style={{
                    padding: '12px',
                    background: colors.bg,
                    border: `3px solid ${colors.border}`,
                    borderRadius: '12px',
                    color: colors.text,
                    minWidth: '200px',
                    boxShadow: course.completed
                      ? '0 4px 6px rgba(0, 0, 0, 0.1)'
                      : '0 2px 4px rgba(0, 0, 0, 0.05)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{course.id}</div>
                      <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '4px' }}>{course.label}</div>
                      <div style={{ fontSize: '11px', opacity: 0.8, marginTop: '4px' }}>
                        {course.credits} credits
                      </div>
                    </div>
                  </div>
                </div>
              ),
            },
            sourcePosition: Position.Right,
            targetPosition: Position.Left,
          });
        });
      });

      const flowEdges: Edge[] = data.edges.map((edge) => ({
        id: edge.id || `${edge.from}-${edge.to}`,
        source: edge.from,
        target: edge.to,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#94a3b8', strokeWidth: 2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#94a3b8',
        },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (error) {
      console.error('Error fetching journey:', error);
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    void fetchJourney();
  }, [fetchJourney]);

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{ fontSize: '24px', marginBottom: '16px' }}>Loading...</div>
        <div>Loading your academic journey...</div>
      </div>
    );
  }

  return (
    <div style={{ height: '85vh', width: '100%' }}>
      <div
        style={{
          padding: '20px',
          background: 'white',
          borderBottom: '1px solid #e5e7eb',
        }}
      >
        <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>Your Academic Journey</h2>
        <p style={{ margin: '8px 0 0 0', color: '#6b7280', fontSize: '14px' }}>
          Visualize your course progression and prerequisites.
        </p>

        <div style={{ display: 'flex', gap: '20px', marginTop: '16px', fontSize: '13px', flexWrap: 'wrap' }}>
          {semesterList.map((semester) => {
            const color = semesterColors.get(semester);
            if (!color) {
              return null;
            }
            return (
              <div key={semester} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div
                  style={{
                    width: '16px',
                    height: '16px',
                    background: color.bg,
                    border: `2px solid ${color.border}`,
                    borderRadius: '4px',
                  }}
                />
                <span>{semester}</span>
              </div>
            );
          })}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>Completed nodes are fully opaque</span>
            <span style={{ marginLeft: '8px' }}>Planned nodes are faded</span>
          </div>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-left"
      >
        <Background color="#e5e7eb" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.id.startsWith('header-')) {
              return '#f3f4f6';
            }
            return '#94a3b8';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  );
};

export default JourneyMap;
