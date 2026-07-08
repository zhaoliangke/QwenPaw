import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface QueueJob {
  id: string;
  case_id: string;
  priority: string;
  status: string;
  retry_count: number;
  shard_id: string;
}

const mockJobs: QueueJob[] = [];

const columns: ColumnsType<QueueJob> = [
  { title: "Job ID", dataIndex: "id", key: "id" },
  { title: "用例ID", dataIndex: "case_id", key: "case_id" },
  {
    title: "优先级",
    dataIndex: "priority",
    key: "priority",
    render: (val: string) => {
      const colors: Record<string, string> = { CRITICAL: "red", HIGH: "orange", NORMAL: "blue", LOW: "default" };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => {
      const colors: Record<string, string> = { passed: "green", failed: "red", running: "blue", queued: "default", retrying: "orange" };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  { title: "重试", dataIndex: "retry_count", key: "retry_count" },
  { title: "分片", dataIndex: "shard_id", key: "shard_id" },
];

export default function ExecutionQueuePage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>执行队列</Title>
        <Paragraph type="secondary">
          优先级队列调度，支持任务分片、智能重试和实时进度追踪。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">总任务</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">运行中</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">通过</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">失败</Paragraph></Card></Col>
      </Row>

      <Card title="队列任务">
        <Table columns={columns} dataSource={mockJobs} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
