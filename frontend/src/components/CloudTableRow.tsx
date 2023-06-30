import React, { useState } from "react";

import { Button, Group, Text } from "@mantine/core";
import { modals } from "@mantine/modals";
import { IconCloudMinus, IconDatabase } from "@tabler/icons-react";

import { ICloudView } from "../core/models/ICloud";

interface CloudTableRowProps {
    cloud: ICloudView;
    makeSync?: (cloud: ICloudView) => Promise<void>;
    makeDelete?: (cloud: ICloudView) => Promise<void>;
}

export function CloudTableRow({ cloud, makeSync, makeDelete }: CloudTableRowProps) {
    const [syncLoading, setSyncLoading] = useState(false);
    const [deleteLoading, setDeleteLoading] = useState(false);

    const onSyncInternal = async () => {
        if (makeSync) {
            setSyncLoading(true);
            await makeSync(cloud);
            setSyncLoading(false);
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
            <td>{cloud.cloud_type}</td>
            <td>
                {cloud.cloud_type === "AWS" && (
                    <>
                        <b>aws_region:</b> {cloud.aws_region} <br />
                        <b>aws_key:</b> {cloud.aws_key}
                    </>
                )}
                {cloud.cloud_type === "AZURE" && (
                    <>
                        <b>azure_subscription_id:</b>{" "}
                        {cloud.azure_subscription_id} <br />
                        <b>azure_tenant_id:</b> {cloud.azure_tenant_id} <br />
                        <b>azure_client_id:</b> {cloud.azure_client_id}
                    </>
                )}
            </td>
            <td>
                <Group spacing="xs">
                    <Button
                        leftIcon={<IconDatabase size="1.125rem" />}
                        color="green"
                        loading={syncLoading}
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
