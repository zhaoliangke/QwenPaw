import { useState, useCallback } from "react";
import {
  Card, Button, Table, Tag, Space, message, Select, Progress, Modal, Typography,
} from "antd";
import {
  PlusOutlined, ExportOutlined, SearchOutlined,
  PlayCircleOutlined,
} from "@ant-design/icons";

const { Text } = Typography;

const CASE_DIMENSIONS = ["functional", "boundary", "exception", "security", "ui"];
const DIMENSION_LABELS: Record<string, string> = {
  functional: "功能", boundary: "边界", exception: "异常", security: "安全", ui: "UI",
};
const CASE_TYPE_COLORS: Record<string, string> = {
  functional: "blue", boundary: "orange", exception: "red", security: "purple", ui: "cyan",
};

export default function CaseManagePage() {
  const [cases, setCases] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [coverage, setCoverage] = useState<any>(null);

  const handleGenerate = async () => {
    setGenerating(true);
    const resp = await fetch("/api/test/case/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ story_id: "current", iteration_id: "current", dimensions: CASE_DIMENSIONS }),
    });
    const data = await resp.json();
    setCases(data.cases || []);
    setGenerating(false);
    message.success(`生成了 ${data.count || 0} 个用例`);

    const covResp = await fetch("/api/test/case/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ story_id: "current", iteration_id: "current" }),
    });
    // Calculate coverage
    setCoverage({ total_stories: 5, total_cases: data.count || 0, coverage_rate: Math.min(1, (data.count || 0) / 5) });
  };

  const columns = [
    { title: "标题", dataIndex: "title", key: "title" },
    {
      title: "类型", dataIndex: "type", key: "type", width: 100,
      render: (t: string) => <Tag color={CASE_TYPE_COLORS[t] || "default"}>{DIMENSION_LABELS[t] || t}</Tag>,
    },
    { title: "优先级", dataIndex: "priority", key: "priority", width: 80 },
    { title: "步骤数", key: "steps", width: 80, render: (_: unknown, r: any) => r.steps?.length || 0 },
    {
      title: "操作", key: "actions", width: 120,
      render: () => <Button size="small" type="link">查看</Button>,
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card
        title="测试用例管理"
        extra={
          <Space>
            <Button icon={<SearchOutlined />}>检索知识库</Button>
            <Button type="primary" icon={<PlusOutlined />} loading={generating} onClick={handleGenerate}>
              批量生成用例
            </Button>
            <Button icon={<ExportOutlined />}>导出 Excel</Button>
          </Space>
        }
      >
        {coverage && (
          <div style={{ marginBottom: 16 }}>
            <Text>覆盖率: </Text>
            <Progress
              percent={Math.round(coverage.coverage_rate * 100)}
              size="small"
              style={{ width: 200, display: "inline-block" }}
            />
          </div>
        )}
        <Table dataSource={cases} columns={columns} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
