import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface NotifyRule {
  id: string;
  name: string;
  triggers: string[];
  channels: string[];
  enabled: boolean;
}

const mockRules: NotifyRule[] = [];

const columns: ColumnsType<NotifyRule> = [
  { title: "规则名称", dataIndex: "name", key: "name" },
  {
    title: "触发事件",
    dataIndex: "triggers",
    key: "triggers",
    render: (val: string[]) => val.map(v => <Tag key={v}>{v}</Tag>),
  },
  {
    title: "通知渠道",
    dataIndex: "channels",
    key: "channels",
    render: (val: string[]) => val.map(v => <Tag key={v} color="blue">{v}</Tag>),
  },
  {
    title: "状态",
    dataIndex: "enabled",
    key: "enabled",
    render: (val: boolean) => <Tag color={val ? "green" : "red"}>{val ? "启用" : "禁用"}</Tag>,
  },
];

export default function NotificationPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>通知告警</Title>
        <Paragraph type="secondary">
          配置通知规则，在测试执行完成/失败/覆盖率下降时通过钉钉、飞书、企微或 Webhook 推送告警。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">通知规则</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">已发送通知</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">失败次数</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>4</Title><Paragraph type="secondary">支持渠道</Paragraph></Card>
        </Col>
      </Row>

      <Card title="通知规则">
        <Table columns={columns} dataSource={mockRules} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
