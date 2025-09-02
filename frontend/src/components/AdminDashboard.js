import React, { useState, useEffect } from 'react';
import { Users, MapPin, Mail, Calendar, Shield, Eye, ToggleLeft, ToggleRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const Card = ({ className = "", children, ...props }) => (
  <div className={`rounded-2xl shadow-lg border border-neutral-200 bg-white ${className}`} {...props}>
    {children}
  </div>
);

const CardContent = ({ className = "", children }) => (
  <div className={`p-5 md:p-6 ${className}`}>
    {children}
  </div>
);

const Button = ({ className = "", variant = "default", children, disabled, ...props }) => {
  const baseClasses = "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = { 
    default: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    outline: "bg-white text-neutral-700 border border-neutral-300 hover:bg-neutral-50 focus:ring-neutral-500",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500"
  };
  return (
    <button 
      className={`${baseClasses} ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`} 
      disabled={disabled} 
      {...props}
    >
      {children}
    </button>
  );
};

const AdminDashboard = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [error, setError] = useState('');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId) => {
    try {
      await axios.post(`${API}/admin/users/${userId}/toggle-status`);
      // Refresh users list
      fetchUsers();
    } catch (error) {
      console.error('Error toggling user status:', error);
      setError('Failed to update user status');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-neutral-600">Loading admin dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-neutral-900">Admin Dashboard</h1>
          </div>
          <p className="text-neutral-600">Welcome back, {user?.first_name}! Manage all user accounts and territories.</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent>
              <div className="flex items-center gap-3">
                <Users className="w-8 h-8 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold text-neutral-900">{users.length}</p>
                  <p className="text-sm text-neutral-600">Total Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <div className="flex items-center gap-3">
                <MapPin className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-2xl font-bold text-neutral-900">
                    {users.reduce((total, user) => total + user.total_territories, 0)}
                  </p>
                  <p className="text-sm text-neutral-600">Total Territories</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <div className="flex items-center gap-3">
                <Users className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-2xl font-bold text-neutral-900">
                    {users.filter(user => user.is_active).length}
                  </p>
                  <p className="text-sm text-neutral-600">Active Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <div className="flex items-center gap-3">
                <Users className="w-8 h-8 text-orange-600" />
                <div>
                  <p className="text-2xl font-bold text-neutral-900">
                    {users.filter(user => !user.is_active).length}
                  </p>
                  <p className="text-sm text-neutral-600">Inactive Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Users Table */}
        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-neutral-900">All Users</h2>
              <Button onClick={fetchUsers}>
                Refresh
              </Button>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-4">
                {error}
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-neutral-200">
                    <th className="text-left py-3 px-4 font-medium text-neutral-900">Name</th>
                    <th className="text-left py-3 px-4 font-medium text-neutral-900">Email</th>
                    <th className="text-left py-3 px-4 font-medium text-neutral-900">Role</th>
                    <th className="text-left py-3 px-4 font-medium text-neutral-900">Territories</th>
                    <th className="text-left py-3 px-4 font-medium text-neutral-900">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-neutral-900">Created</th>
                    <th className="text-left py-3 px-4 font-medium text-neutral-900">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((userData) => (
                    <tr key={userData.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                      <td className="py-3 px-4">
                        <div className="font-medium text-neutral-900">
                          {userData.first_name} {userData.last_name}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2 text-neutral-600">
                          <Mail className="w-4 h-4" />
                          {userData.email}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                          userData.role === 'super_admin' 
                            ? 'bg-purple-100 text-purple-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          <Shield className="w-3 h-3" />
                          {userData.role}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-neutral-400" />
                          <span className="font-medium">{userData.total_territories}</span>
                          {userData.owned_territories.length > 0 && (
                            <div className="text-xs text-neutral-500">
                              ({userData.owned_territories.join(', ')})
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                          userData.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {userData.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2 text-neutral-600 text-sm">
                          <Calendar className="w-4 h-4" />
                          {formatDate(userData.created_at)}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            onClick={() => setSelectedUser(userData)}
                            className="text-xs"
                          >
                            <Eye className="w-3 h-3" />
                            View
                          </Button>
                          <Button
                            variant={userData.is_active ? "danger" : "default"}
                            onClick={() => toggleUserStatus(userData.id)}
                            className="text-xs"
                          >
                            {userData.is_active ? (
                              <>
                                <ToggleRight className="w-3 h-3" />
                                Deactivate
                              </>
                            ) : (
                              <>
                                <ToggleLeft className="w-3 h-3" />
                                Activate
                              </>
                            )}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {users.length === 0 && (
              <div className="text-center py-8 text-neutral-500">
                No users found.
              </div>
            )}
          </CardContent>
        </Card>

        {/* User Detail Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="max-w-2xl w-full max-h-96 overflow-y-auto">
              <CardContent>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-neutral-900">User Details</h3>
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="text-neutral-400 hover:text-neutral-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Full Name</label>
                      <div className="text-neutral-900">{selectedUser.first_name} {selectedUser.last_name}</div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Email</label>
                      <div className="text-neutral-900">{selectedUser.email}</div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Role</label>
                      <div className="text-neutral-900">{selectedUser.role}</div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Status</label>
                      <div className="text-neutral-900">{selectedUser.account_status}</div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-1">Owned Territories</label>
                    <div className="text-neutral-900">
                      {selectedUser.owned_territories.length > 0 
                        ? selectedUser.owned_territories.join(', ') 
                        : 'No territories assigned'}
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Account Created</label>
                      <div className="text-neutral-900">{formatDate(selectedUser.created_at)}</div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Total Territories</label>
                      <div className="text-neutral-900">{selectedUser.total_territories}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;