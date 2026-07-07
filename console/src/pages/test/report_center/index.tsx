import { useState } from "react";
import {
  Card, Button, Table, Space, message, Tag, Progress, Statistic, Row, Col,
} from "antd";
import {
  BarChartOutlined, SendOutlined, DownloadOutlined,
  FileProtectOutlined,
} from "@ant-design/icons";

export default function ReportCenterPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    const resp = await fetch("/api/test/report/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        test_run: {
          id: "tr-sample",
          results: [
            { case_id: "tc-001", status: "passed", duration_ms: 120 },
            { case_id: "tc-002", status: "failed", duration_ms: 80, log: "Assertion failed" },
            { case_id: "tc-003", status: "passed", duration_ms: 95 },
          ],
        },
        iteration_id: "current",
      }),
    });
    const data = await resp.json();
    setReports(prev => [data, ...prev]);
    setGenerating(false);
    message.success("报告生成成功");
  };

  const handlePush = async (reportId: string) => {
    await fetch(`/api/test/report/push/${reportId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channels: ["dingtalk"] }),
    });
    message.success("报告已推送至钉钉");
  };

  const columns = [
    { title: "报告 ID", dataIndex: "id", key: "id", width: 200 },
    {
      title: "通过率", key: "pass_rate", width: 120,
      render: (_: unknown, r: any) => (
        <Progress percent={Math.round((r.pass_rate || 0) * 100)} size="small"
          status={r.pass_rate === 1 ? "success" : "exception"} />
      ),
    },
    { title: "用例数", dataIndex: "total_cases", key: "total", width: 80 },
    { title: "通过", dataIndex: "passed", key: "passed", width: 60, render: (v: number) => <Tag color="green">{v}</Tag> },
    { title: "失败", dataIndex: "failed", key: "failed", width: 60, render: (v: number) => <Tag color="red">{v}</Tag> },
    { title: "生成时间", dataIndex: "generated_at", key: "time", width: 180 },
    {
      title: "操作", key: "actions", width: 200,
      render: (_: unknown, r: any) => (
        <Space size="small">
          <Button size="small" icon={<DownloadOutlined />}>下载</Button>
          <Button size="small" icon={<SendOutlined />} onClick={() => handlePush(r.id)}>推送</Button>
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card title="测试报告中心" extra={
        <Space>
          <Button type="primary" icon={<BarChartOutlined />} loading={generating} onClick={handleGenerate}>
            生成报告
          </Button>
        </Space>
      }>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}><Statistic title="总报告数" value={reports.length} prefix={<FileProtectOutlined />} /></Col>
          <Col span={6}><Statistic title="平均通过率" value={reports.length ? "67%" : "-"} /></Col>
        </Row>
        <Table dataSource={reports} columns={columns} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
