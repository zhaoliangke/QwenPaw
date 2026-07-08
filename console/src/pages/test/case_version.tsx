import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface CaseVersion {
  id: string;
  version: number;
  change_type: string;
  changes_count: number;
  comment: string;
  created_at: string;
}

const mockVersions: CaseVersion[] = [];

const columns: ColumnsType<CaseVersion> = [
  {
    title: "版本",
    dataIndex: "version",
    key: "version",
    render: (val: number) => <Tag color="blue">v{val}</Tag>,
  },
  {
    title: "变更类型",
    dataIndex: "change_type",
    key: "change_type",
    render: (val: string) => {
      const colors: Record<string, string> = { created: "green", updated: "blue", rolled_back: "orange" };
      const labels: Record<string, string> = { created: "创建", updated: "更新", rolled_back: "回滚" };
      return <Tag color={colors[val] || "default"}>{labels[val] || val}</Tag>;
    },
  },
  { title: "变更字段数", dataIndex: "changes_count", key: "changes_count" },
  { title: "备注", dataIndex: "comment", key: "comment" },
  { title: "时间", dataIndex: "created_at", key: "created_at" },
];

export default function CaseVersionPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>用例版本控制</Title>
        <Paragraph type="secondary">
          追踪测试用例变更历史，支持版本对比 (diff) 和回滚到任意历史版本。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">版本快照</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">回滚次数</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">对比次数</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">追踪用例</Paragraph></Card></Col>
      </Row>

      <Card title="版本历史">
        <Table columns={columns} dataSource={mockVersions} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
