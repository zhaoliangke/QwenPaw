import { useState, useCallback } from "react";
import {
  Card, Button, Table, Space, message, Progress, InputNumber, Tag, Collapse,
} from "antd";
import {
  ThunderboltOutlined, ReloadOutlined, PlayCircleOutlined,
  CheckCircleOutlined, CloseCircleOutlined,
} from "@ant-design/icons";

export default function TestExecPage() {
  const [runs, setRuns] = useState<any[]>([]);
  const [activeRun, setActiveRun] = useState<any>(null);
  const [executing, setExecuting] = useState(false);
  const [concurrency, setConcurrency] = useState(4);

  const handleBatchRun = async () => {
    setExecuting(true);
    const resp = await fetch("/api/test/exec/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_ids: ["tc-001", "tc-002", "tc-003"],
        iteration_id: "current",
        concurrency,
        environment: "test",
      }),
    });
    const data = await resp.json();
    setActiveRun(data);
    setRuns(prev => [data, ...prev]);
    setExecuting(false);
    message.success(`批量执行已启动: ${data.id}`);
  };

  const handleRefresh = async () => {
    if (!activeRun) return;
    const resp = await fetch(`/api/test/exec/progress/${activeRun.id}`);
    const data = await resp.json();
    setActiveRun(data);
  };

  const columns = [
    { title: "Run ID", dataIndex: "id", key: "id", width: 200 },
    { title: "环境", dataIndex: "environment", key: "environment", width: 100 },
    { title: "用例数", key: "cases", width: 100, render: (_: unknown, r: any) => r.case_ids?.length || 0 },
    {
      title: "状态", dataIndex: "status", key: "status", width: 100,
      render: (s: string) => <Tag color={s === "completed" ? "green" : "processing"}>{s}</Tag>,
    },
    {
      title: "操作", key: "actions", width: 150,
      render: (_: unknown, r: any) => (
        <Space size="small">
          <Button size="small" icon={<ReloadOutlined />} onClick={handleRefresh}>刷新</Button>
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card title="测试执行调度" extra={
        <Space>
          <span>并发:</span>
          <InputNumber min={1} max={16} value={concurrency} onChange={v => setConcurrency(v || 4)} />
          <Button type="primary" icon={<ThunderboltOutlined />} loading={executing} onClick={handleBatchRun}>
            批量执行
          </Button>
        </Space>
      }>
        {activeRun && (
          <Card size="small" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Progress percent={activeRun.progress_pct || 0} status={activeRun.status === "completed" ? "success" : "active"} />
              <Space>
                <Tag icon={<CheckCircleOutlined />} color="green">通过: {activeRun.passed || 0}</Tag>
                <Tag icon={<CloseCircleOutlined />} color="red">失败: {activeRun.failed || 0}</Tag>
                <Tag>总数: {activeRun.total || 0}</Tag>
              </Space>
            </Space>
          </Card>
        )}
        <Table dataSource={runs} columns={columns} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
