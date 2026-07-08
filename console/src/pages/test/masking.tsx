import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface MaskFinding {
  field: string;
  type: string;
  sample: string;
}

const mockFindings: MaskFinding[] = [];

const columns: ColumnsType<MaskFinding> = [
  { title: "字段名", dataIndex: "field", key: "field" },
  {
    title: "敏感类型",
    dataIndex: "type",
    key: "type",
    render: (val: string) => {
      const colors: Record<string, string> = {
        phone: "blue", email: "cyan", id_card: "orange", bank_card: "gold",
        password: "red", token: "magenta", name: "purple", address: "geekblue",
      };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  { title: "示例值", dataIndex: "sample", key: "sample" },
];

export default function MaskingPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>数据脱敏</Title>
        <Paragraph type="secondary">
          识别手机号/邮箱/身份证/银行卡/密码等敏感字段，对测试日志和报告中的敏感数据进行脱敏处理。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>8</Title><Paragraph type="secondary">内置规则</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">已脱敏字段</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">脱敏次数</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>8</Title><Paragraph type="secondary">字段类型</Paragraph></Card></Col>
      </Row>

      <Card title="敏感字段检测结果">
        <Table columns={columns} dataSource={mockFindings} rowKey="field" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
