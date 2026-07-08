import { useState, useEffect, useCallback } from "react";
import {
  Card, Table, Button, Modal, Form, Input, Select,
  Tag, Space, message, Popconfirm, Descriptions,
} from "antd";
import { PlusOutlined, ReloadOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from "@ant-design/icons";
import { api } from "../../../api";

const { Option } = Select;
const { TextArea } = Input;

interface ElementMap {
  id: string;
  project_id: string;
  page_name: string;
  mapping: Record<string, string>;
  created_at: string;
  updated_at: string;
}

interface Project {
  id: string;
  name: string;
  target_url: string;
}

export default function ElementMapPage() {
  const [maps, setMaps] = useState<ElementMap[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editing, setEditing] = useState<ElementMap | null>(null);
  const [detailItem, setDetailItem] = useState<ElementMap | null>(null);
  const [mappingEntries, setMappingEntries] = useState<Array<{ key: string; value: string }>>([]);
  const [form] = Form.useForm();

  const fetchMaps = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.listElementMaps();
      setMaps(res.element_maps || []);
    } catch {
      message.error("加载元素映射列表失败");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchProjects = useCallback(async () => {
    try {
      const res = await api.projectApi.listProjects();
      setProjects(res.projects || []);
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    fetchMaps();
    fetchProjects();
  }, [fetchMaps, fetchProjects]);

  function openCreate() {
    setEditing(null);
    setMappingEntries([{ key: "", value: "" }]);
    form.resetFields();
    setModalOpen(true);
  }

  function openEdit(record: ElementMap) {
    setEditing(record);
    const entries = Object.entries(record.mapping).map(([k, v]) => ({ key: k, value: v }));
    setMappingEntries(entries.length > 0 ? entries : [{ key: "", value: "" }]);
    form.setFieldsValue({
      project_id: record.project_id,
      page_name: record.page_name,
    });
    setModalOpen(true);
  }

  function openDetail(record: ElementMap) {
    setDetailItem(record);
    setDetailOpen(true);
  }

  function addMappingRow() {
    setMappingEntries(prev => [...prev, { key: "", value: "" }]);
  }

  function removeMappingRow(index: number) {
    setMappingEntries(prev => prev.filter((_, i) => i !== index));
  }

  function updateMappingKey(index: number, k: string) {
    setMappingEntries(prev => prev.map((e, i) => (i === index ? { ...e, key: k } : e)));
  }

  function updateMappingValue(index: number, v: string) {
    setMappingEntries(prev => prev.map((e, i) => (i === index ? { ...e, value: v } : e)));
  }

  async function handleSubmit() {
    try {
      const values = await form.validateFields();
      const mapping: Record<string, string> = {};
      mappingEntries.forEach(e => {
        if (e.key.trim()) {
          mapping[e.key.trim()] = e.value.trim();
        }
      });
      if (editing) {
        await api.updateElementMap(editing.id, {
          project_id: values.project_id,
          page_name: values.page_name,
          mapping,
        });
        message.success("元素映射已更新");
      } else {
        await api.createElementMap({
          project_id: values.project_id,
          page_name: values.page_name,
          mapping,
        });
        message.success("元素映射已创建");
      }
      setModalOpen(false);
      fetchMaps();
    } catch {
      message.error("保存失败");
    }
  }

  async function handleDelete(id: string) {
    try {
      await api.deleteElementMap(id);
      message.success("已删除");
      fetchMaps();
    } catch {
      message.error("删除失败");
    }
  }

  function getProjectName(projectId: string): string {
    const p = projects.find(x => x.id === projectId);
    return p ? p.name : projectId;
  }

  const columns = [
    { title: "页面名称", dataIndex: "page_name", key: "page_name" },
    {
      title: "所属项目",
      dataIndex: "project_id",
      key: "project_id",
      render: (id: string) => getProjectName(id) || id,
    },
    {
      title: "映射条目数",
      key: "count",
      render: (_: unknown, record: ElementMap) => Object.keys(record.mapping).length,
    },
    {
      title: "更新时间",
      dataIndex: "updated_at",
      key: "updated_at",
      render: (t: string) => t?.slice(0, 19)?.replace("T", " ") || "-",
    },
    {
      title: "操作",
      key: "actions",
      width: 200,
      render: (_: unknown, record: ElementMap) => (
        <Space>
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => openDetail(record)}>
            查看
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="元素映射管理"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchMaps}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建映射</Button>
        </Space>
      }
    >
      <Table
        rowKey="id"
        columns={columns}
        dataSource={maps}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      {/* Create / Edit Modal */}
      <Modal
        title={editing ? "编辑元素映射" : "新建元素映射"}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        width={640}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="project_id" label="所属项目" rules={[{ required: true, message: "请选择项目" }]}>
            <Select placeholder="选择项目" showSearch optionFilterProp="children">
              {projects.map(p => (
                <Option key={p.id} value={p.id}>{p.name} ({p.target_url})</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="page_name" label="页面名称" rules={[{ required: true, message: "请输入页面名称" }]}>
            <Input placeholder="例如: login, dashboard, user-profile" />
          </Form.Item>
          <Form.Item label="元素映射">
            <div style={{ marginBottom: 8, color: "#666", fontSize: 12 }}>
              每行一条：元素名称 → 选择器（data-testid / CSS / XPath）
            </div>
            {mappingEntries.map((entry, i) => (
              <Space key={i} style={{ display: "flex", marginBottom: 8 }} align="start">
                <Input
                  placeholder="元素名称"
                  value={entry.key}
                  onChange={e => updateMappingKey(i, e.target.value)}
                  style={{ width: 140 }}
                />
                <Input
                  placeholder='选择器 例如: [data-testid="login-btn"]'
                  value={entry.value}
                  onChange={e => updateMappingValue(i, e.target.value)}
                  style={{ width: 340 }}
                />
                <Button danger size="small" onClick={() => removeMappingRow(i)} disabled={mappingEntries.length <= 1}>
                  删除
                </Button>
              </Space>
            ))}
            <Button type="dashed" size="small" onClick={addMappingRow} style={{ marginTop: 4 }}>
              + 添加一行
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Detail Modal */}
      <Modal
        title="元素映射详情"
        open={detailOpen}
        onCancel={() => setDetailOpen(false)}
        footer={null}
        width={560}
      >
        {detailItem && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="页面名称">{detailItem.page_name}</Descriptions.Item>
            <Descriptions.Item label="所属项目">{getProjectName(detailItem.project_id)}</Descriptions.Item>
            <Descriptions.Item label="创建时间">{detailItem.created_at?.slice(0, 19)?.replace("T", " ")}</Descriptions.Item>
            <Descriptions.Item label="更新时间">{detailItem.updated_at?.slice(0, 19)?.replace("T", " ")}</Descriptions.Item>
            <Descriptions.Item label="元素映射">
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#fafafa" }}>
                    <th style={{ padding: "4px 8px", border: "1px solid #f0f0f0", textAlign: "left" }}>元素名称</th>
                    <th style={{ padding: "4px 8px", border: "1px solid #f0f0f0", textAlign: "left" }}>选择器</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(detailItem.mapping).map(([k, v]) => (
                    <tr key={k}>
                      <td style={{ padding: "4px 8px", border: "1px solid #f0f0f0" }}><Tag>{k}</Tag></td>
                      <td style={{ padding: "4px 8px", border: "1px solid #f0f0f0", fontFamily: "monospace", fontSize: 12 }}>{v}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </Card>
  );
}
