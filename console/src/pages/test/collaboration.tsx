import { Card, Col, Row, Space, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface AuditEntry {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  user: string;
  details: string;
  created_at: string;
}

const mockLogs: AuditEntry[] = [];

const columns: ColumnsType<AuditEntry> = [
  { title: "动作", dataIndex: "action", key: "action" },
  { title: "资源类型", dataIndex: "resource_type", key: "resource_type" },
  { title: "资源ID", dataIndex: "resource_id", key: "resource_id" },
  { title: "操作人", dataIndex: "user", key: "user" },
  { title: "详情", dataIndex: "details", key: "details" },
  { title: "时间", dataIndex: "created_at", key: "created_at" },
];

export default function CollaborationPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>多人协作</Title>
        <Paragraph type="secondary">
          评论、任务分配、操作审计，支持团队协作和权限追踪。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">评论数</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">待办任务</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">审计记录</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">团队成员</Paragraph></Card></Col>
      </Row>

      <Card title="操作审计">
        <Table columns={columns} dataSource={mockLogs} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
