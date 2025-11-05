import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  StockOutlined,
  BarChartOutlined,
  StarOutlined
} from '@ant-design/icons'
import Dashboard from './components/Dashboard'
import StockList from './components/StockList'
import IndustryView from './components/IndustryView'
import Recommendation from './components/Recommendation'
import './App.css'

const { Header, Content, Sider } = Layout

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          Graham Value Investment Analyzer
        </div>
      </Header>
      <Layout>
        <Sider width={200} theme="light">
          <Menu
            mode="inline"
            defaultSelectedKeys={['1']}
            style={{ height: '100%', borderRight: 0 }}
            items={[
              {
                key: '1',
                icon: <DashboardOutlined />,
                label: '仪表盘',
                onClick: () => window.location.href = '/'
              },
              {
                key: '2',
                icon: <BarChartOutlined />,
                label: '行业分析',
                onClick: () => window.location.href = '/industries'
              },
              {
                key: '3',
                icon: <StockOutlined />,
                label: '个股分析',
                onClick: () => window.location.href = '/stocks'
              },
              {
                key: '4',
                icon: <StarOutlined />,
                label: '推荐列表',
                onClick: () => window.location.href = '/recommendations'
              }
            ]}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff'
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/industries" element={<IndustryView />} />
              <Route path="/stocks" element={<StockList />} />
              <Route path="/recommendations" element={<Recommendation />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

export default App
