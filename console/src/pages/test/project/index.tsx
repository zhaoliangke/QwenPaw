import { useState, useEffect, useCallback } from "react";
import {
  Card, Table, Button, Modal, Form, Input, Select,
  Tag, Space, message, Popconfirm,
} from "antd";
import { PlusOutlined, ReloadOutlined, EditOutlined, DeleteOutlined, LinkOutlined } from "@ant-design/icons";
import { api } from "../../../api";

const { Option } = Select;

interface Project {
  id: string;
  name: string;
  target_url: string;
  description?: string;
  env: string;
  tags: string[];
  owner: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const ENV_OPTIONS = [
  { value: "test", label: "测试环境", color: "blue" },
  { value: "staging", label: "预发环境", color: "orange" },
  { value: "prod", label: "生产环境", color: "red" },
];

const ENV_COLORS: Record<string, string> = {};
ENV_OPTIONS.forEach(o => { ENV_COLORS[o.value] = o.color; });

export default function ProjectPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Project | null>(null);
  const [form] = Form.useForm();

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.listProjects();
      setProjects(res.projects || []);
    } catch {
      message.error("加载项目列表失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

  const handleCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const handleEdit = (record: Project) => {
    setEditing(record);
    form.setFieldsValue({
      name: record.name,
      target_url: record.target_url,
      description: record.description,
      env: record.env,
      tags: record.tags?.join(", "),
      owner: record.owner,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        name: values.name,
        target_url: values.target_url,
        description: values.description || "",
        env: values.env || "test",
        tags: values.tags ? String(values.tags).split(",").map((t: string) => t.trim()).filter(Boolean) : [],
        owner: values.owner || "",
      };
      if (editing) {
        await api.updateProject(editing.id, payload);
        message.success("项目更新成功");
      } else {
        await api.createProject(payload);
        message.success("项目创建成功");
      }
      setModalOpen(false);
      fetchProjects();
    } catch (e) {
      if (e?.errorFields) return;
      message.error("操作失败");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteProject(id);
      message.success("项目已删除");
      fetchProjects();
    } catch {
      message.error("删除失败");
    }
  };

  const columns = [
    {
      title: "项目名称",
      dataIndex: "name",
      key: "name",
      render: (name: string, record: Project) => (
        <Space>
          <span>{name}</span>
          {record.target_url && (
            <a href={record.target_url} target="_blank" rel="noreferrer" style={{ fontSize: 12, color: "#1677ff" }}>
              <LinkOutlined />
            </a>
          )}
        </Space>
      ),
    },
    {
      title: "环境",
      dataIndex: "env",
      key: "env",
      width: 100,
      render: (env: string) => <Tag color={ENV_COLORS[env] || "default"}>{env || "test"}</Tag>,
    },
    {
      title: "Tags",
      dataIndex: "tags",
      key: "tags",
      width: 160,
      render: (tags: string[]) => (
        <Space size={2} wrap>
          {(tags || []).map((t) => <Tag key={t} style={{ fontSize: 10 }}>{t}</Tag>)}
        </Space>
      ),
    },
    {
      title: "负责人",
      dataIndex: "owner",
      key: "owner",
      width: 100,
    },
    {
      title: "更新时间",
      dataIndex: "updated_at",
      key: "updated_at",
      width: 160,
      render: (t: string) => t?.slice(0, 19)?.replace("T", " ") || "-",
    },
    {
      title: "操作",
      key: "actions",
      width: 140,
      render: (_: unknown, record: Project) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除该项目？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="项目管理"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchProjects}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新建项目</Button>
        </Space>
      }
    >
      <Table
        rowKey="id"
        columns={columns}
        dataSource={projects}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
      <Modal
        title={editing ? "编辑项目" : "新建项目"}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="name" label="项目名称" rules={[{ required: true, message: "请输入项目名称" }]}>
            <Input placeholder="例如: 电商平台" />
          </Form.Item>
          <Form.Item name="target_url" label="目标地址" rules={[{ required: true, message: "请输入目标地址" }]}>
            <Input placeholder="https://example.com" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} placeholder="项目描述（可选）" />
          </Form.Item>
          <Form.Item name="env" label="环境" initialValue="test">
            <Select>
              <Option value="test">测试环境</Option>
              <Option value="staging">预发环境</Option>
              <Option value="prod">生产环境</Option>
            </Select>
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Input placeholder="多个标签用逗号分隔" />
          </Form.Item>
          <Form.Item name="owner" label="负责人">
            <Input placeholder="负责人（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}