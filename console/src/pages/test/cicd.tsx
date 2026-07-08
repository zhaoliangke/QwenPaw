import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface HookEvent {
  id: string;
  event_type: string;
  branch: string;
  commit_sha: string;
  author: string;
  received_at: string;
  status: string;
}

const mockEvents: HookEvent[] = [];

const columns: ColumnsType<HookEvent> = [
  { title: "事件类型", dataIndex: "event_type", key: "event_type" },
  { title: "分支", dataIndex: "branch", key: "branch" },
  { title: "Commit", dataIndex: "commit_sha", key: "commit_sha" },
  { title: "作者", dataIndex: "author", key: "author" },
  { title: "接收时间", dataIndex: "received_at", key: "received_at" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => (
      <Tag color={val === "processed" ? "green" : val === "received" ? "blue" : "default"}>
        {val}
      </Tag>
    ),
  },
];

export default function CICDPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>CI/CD 集成</Title>
        <Paragraph type="secondary">
          接收 GitHub/GitLab webhook 事件，自动触发测试执行。提供 Actions 和 GitLab CI 配置模板。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">Webhook 配置</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">已处理事件</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">自动触发次数</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>2</Title>
            <Paragraph type="secondary">CI 模板</Paragraph>
          </Card>
        </Col>
      </Row>

      <Card title="事件日志">
        <Table columns={columns} dataSource={mockEvents} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
