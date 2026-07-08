import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface EnvItem {
  id: string;
  name: string;
  base_url: string;
  status: string;
  response_time_ms: number;
}

const mockEnvs: EnvItem[] = [];

const columns: ColumnsType<EnvItem> = [
  { title: "环境名称", dataIndex: "name", key: "name" },
  { title: "Base URL", dataIndex: "base_url", key: "base_url" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => {
      const m: Record<string, string> = { ready: "green", busy: "blue", down: "red", unknown: "default" };
      const labels: Record<string, string> = { ready: "就绪", busy: "占用", down: "不可用", unknown: "未知" };
      return <Tag color={m[val] || "default"}>{labels[val] || val}</Tag>;
    },
  },
  {
    title: "响应时间",
    dataIndex: "response_time_ms",
    key: "response_time_ms",
    render: (val: number) => val ? `${val.toFixed(0)}ms` : "-",
  },
];

export default function EnvironmentPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>测试环境管理</Title>
        <Paragraph type="secondary">
          注册测试环境，配置健康检查 URL，实时监控环境可用性和响应时间。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">已注册环境</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">可用环境</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">不可用环境</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>-</Title><Paragraph type="secondary">平均响应</Paragraph></Card>
        </Col>
      </Row>

      <Card title="环境列表">
        <Table columns={columns} dataSource={mockEnvs} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
