import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface ChaosResult {
  id: string;
  status: string;
  impact_score: number;
  error_rate_before: number;
  error_rate_during: number;
  recovery_time_ms: number;
}

const mockResults: ChaosResult[] = [];

const columns: ColumnsType<ChaosResult> = [
  { title: "结果ID", dataIndex: "id", key: "id" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => {
      const colors: Record<string, string> = { completed: "green", failed: "red", injecting: "blue" };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  {
    title: "影响分",
    dataIndex: "impact_score",
    key: "impact_score",
    render: (val: number) => {
      const color = val > 0.5 ? "red" : val > 0.1 ? "orange" : "green";
      return <Tag color={color}>{(val * 100).toFixed(0)}</Tag>;
    },
  },
  {
    title: "错误率变化",
    key: "error_rate",
    render: (_: any, row: ChaosResult) => (
      <span>{(row.error_rate_before * 100).toFixed(0)}% → {(row.error_rate_during * 100).toFixed(0)}%</span>
    ),
  },
  {
    title: "恢复时间",
    dataIndex: "recovery_time_ms",
    key: "recovery_time_ms",
    render: (val: number) => `${(val / 1000).toFixed(1)}s`,
  },
];

export default function ChaosPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>混沌工程注入</Title>
        <Paragraph type="secondary">
          注入网络延迟/丢包/错误/资源压力/DNS 故障/时钟偏移，测量系统韧性和恢复能力。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">实验数</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>6</Title><Paragraph type="secondary">故障类型</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">已完成</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">发现数</Paragraph></Card></Col>
      </Row>

      <Card title="实验结果">
        <Table columns={columns} dataSource={mockResults} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
