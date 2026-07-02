import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Globe, Lock, Trash2, UserPlus, Users } from "lucide-react";

import { workspacesApi } from "@/api/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";

export function AdminWorkspaceSettingsPage() {
  const { workspaceId } = useParams();
  const queryClient = useQueryClient();
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");

  const { data: workspace, isLoading } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => workspacesApi.get(workspaceId!).then((r) => r.data),
    enabled: !!workspaceId,
  });

  const updateMutation = useMutation({
    mutationFn: (data: object) => workspacesApi.update(workspaceId!, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workspace", workspaceId] }),
  });

  const inviteMutation = useMutation({
    mutationFn: () => workspacesApi.addMember(workspaceId!, inviteEmail, inviteRole),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workspace", workspaceId] });
      setIsInviteOpen(false);
      setInviteEmail("");
      setInviteRole("member");
    },
  });

  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) => workspacesApi.removeMember(workspaceId!, userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workspace", workspaceId] }),
  });

  const changeRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      workspacesApi.changeRole(workspaceId!, userId, role),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workspace", workspaceId] }),
  });

  if (isLoading || !workspace) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-48" />
        <Skeleton className="h-48" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Workspace settings</h1>
        <p className="text-sm text-gray-500">Manage visibility, members, and sharing.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {workspace.is_public ? <Globe className="h-5 w-5" /> : <Lock className="h-5 w-5" />}
            Visibility
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-4">
            <div>
              <p className="font-medium text-gray-900">
                {workspace.is_public ? "Public workspace" : "Private workspace"}
              </p>
              <p className="text-sm text-gray-500">
                {workspace.is_public
                  ? "Anyone with the link can view boards, roadmap, and changelog."
                  : "Only invited team members can access this workspace."}
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => updateMutation.mutate({ is_public: !workspace.is_public })}
              isLoading={updateMutation.isPending}
            >
              {workspace.is_public ? "Make private" : "Make public"}
            </Button>
          </div>

          <div>
            <p className="mb-1 text-sm font-medium text-gray-700">Public link</p>
            <Input
              readOnly
              value={`${window.location.origin}/w/${workspace.slug}`}
              onFocus={(e) => e.target.select()}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Members
          </CardTitle>
          <Button size="sm" onClick={() => setIsInviteOpen(true)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Invite
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {workspace.members?.map((member) => (
            <div
              key={member.id}
              className="flex items-center justify-between rounded-lg border border-gray-100 p-3"
            >
              <div>
                <p className="font-medium text-gray-900">{member.full_name}</p>
                <p className="text-sm text-gray-500">{member.email}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="neutral">{member.role}</Badge>
                <Select
                  value={member.role}
                  onChange={(e) =>
                    changeRoleMutation.mutate({ userId: member.user_id, role: e.target.value })
                  }
                  options={[
                    { value: "member", label: "Member" },
                    { value: "admin", label: "Admin" },
                    { value: "owner", label: "Owner" },
                  ]}
                  className="w-32"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeMemberMutation.mutate(member.user_id)}
                >
                  <Trash2 className="h-4 w-4 text-red-600" />
                </Button>
              </div>
            </div>
          ))}
          {!workspace.members?.length && <p className="text-sm text-gray-500">No other members.</p>}
        </CardContent>
      </Card>

      <Modal isOpen={isInviteOpen} onClose={() => setIsInviteOpen(false)} title="Invite member">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            inviteMutation.mutate();
          }}
          className="space-y-4"
        >
          <Input
            label="Email"
            type="email"
            required
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
          />
          <Select
            label="Role"
            value={inviteRole}
            onChange={(e) => setInviteRole(e.target.value)}
            options={[
              { value: "member", label: "Member" },
              { value: "admin", label: "Admin" },
            ]}
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setIsInviteOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={inviteMutation.isPending}>
              Invite
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
