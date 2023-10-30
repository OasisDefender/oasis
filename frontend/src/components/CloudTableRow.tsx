import React, { useState } from "react";

import { Button, Group, Stack, Text } from "@mantine/core";
import { modals } from "@mantine/modals";
import { IconCloudMinus, IconDatabase } from "@tabler/icons-react";

import { ICloudView, SyncState } from "../core/models/ICloud";

interface CloudTableRowProps {
    cloud: ICloudView;
    makeSync?: (cloud: ICloudView) => Promise<void>;
    makeDelete?: (cloud: ICloudView) => Promise<void>;
    onRefresh?: () => Promise<void>;
    infoShowed: boolean;
}

export function CloudTableRow({
    cloud,
    makeSync,
    makeDelete,
    onRefresh,
    infoShowed,
}: CloudTableRowProps) {
    const [syncLoading, setSyncLoading] = useState(false);
    const [deleteLoading, setDeleteLoading] = useState(false);

    const onSyncInternal = async () => {
        if (makeSync) {
            setSyncLoading(true);
            await makeSync(cloud);
            setSyncLoading(false);
            onRefresh?.();
        }
    };

    const onDeleteInternal = async () => {
        if (makeDelete) {
            modals.openConfirmModal({
                title: "Delete your cloud",
                centered: true,
                children: (
                    <Text size="sm">
                        Are you sure you want to delete your cloud?
                    </Text>
                ),
                labels: {
                    confirm: "Delete cloud",
                    cancel: "No, don't delete it",
                },
                confirmProps: { color: "red" },
                onConfirm: async () => {
                    setDeleteLoading(true);
                    await makeDelete(cloud);
                    setDeleteLoading(false);
                },
            });
        }
    };

    return (
        <tr key={cloud.id}>
            <td>{cloud.name}</td>
            <td>
                <b>Cloud type:</b> {cloud.cloud_type} <br />
                {cloud.cloud_type === "AWS" && (
                    <>
                        <b>Region:</b> {cloud.aws_region} <br />
                        {infoShowed && (
                            <>
                                <b>aws_key:</b> {cloud.aws_key}
                            </>
                        )}
                    </>
                )}
                {cloud.cloud_type === "AZURE" && (
                    <>
                        {infoShowed && (
                            <>
                                <b>Subscription ID:</b>{" "}
                                {cloud.azure_subscription_id}
                                <br />
                                <b>azure_tenant_id:</b> {cloud.azure_tenant_id}
                                <br />
                                <b>azure_client_id:</b> {cloud.azure_client_id}
                            </>
                        )}
                    </>
                )}
            </td>
            <td>
                <Stack spacing="xs">
                    {cloud.sync_state == SyncState.InSync && (
                        <Text>
                            Sync in progress. Press "Refresh" to update the
                            status. <br />
                        </Text>
                    )}
                    {cloud.last_successful_sync && (
                        <Text>
                            <b>Last successful sync:</b> {cloud.sync_stop}
                        </Text>
                    )}
                    {cloud.sync_state == SyncState.InSync &&
                        cloud.sync_start && (
                            <Text>
                                <b>The sync was started at:</b>{" "}
                                {cloud.sync_start}
                            </Text>
                        )}
                    {cloud.sync_stop && (
                        <Text>
                            <b>The sync was finished at:</b> {cloud.sync_stop}
                        </Text>
                    )}
                    {cloud.sync_state == SyncState.Synced && cloud.sync_msg && (
                        <Text color="red">
                            <b>Sync error:</b> {cloud.sync_msg}
                        </Text>
                    )}
                </Stack>
            </td>
            <td>
                <Group spacing="xs">
                    <Button
                        leftIcon={<IconDatabase size="1.125rem" />}
                        color="green"
                        loading={
                            cloud.sync_state == SyncState.InSync || syncLoading
                        }
                        disabled={deleteLoading}
                        onClick={onSyncInternal}
                    >
                        Sync
                    </Button>
                    <Button
                        leftIcon={<IconCloudMinus size="1.125rem" />}
                        color="red"
                        loading={deleteLoading}
                        disabled={syncLoading}
                        onClick={onDeleteInternal}
                    >
                        Delete
                    </Button>
                </Group>
            </td>
        </tr>
    );
}
