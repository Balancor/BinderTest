#include <stdio.h>
#include <linux/types.h>
#include <linux/binder.h>

#define B_PACK_CHARS(c1, c2, c3, c4) \
    ((((c1)<<24)) | (((c2)<<16)) | (((c3)<<8)) | (c4))

int main(){
    printf("B_PACK_CHARS: %d\n", B_PACK_CHARS('_','P','N','G'));
    printf("%d",BR_ERROR);
    printf("%d",BR_OK);
    printf("%d",BR_TRANSACTION);
    printf("%d",BR_REPLY);
    printf("%d",BR_ACQUIRE_RESULT);
    printf("%d",BR_DEAD_REPLY);
    printf("%d",BR_TRANSACTION_COMPLETE);
    printf("%d",BR_INCREFS);
    printf("%d",BR_ACQUIRE);
    printf("%d",BR_RELEASE);
    printf("%d",BR_DECREFS);
    printf("%d",BR_ATTEMPT_ACQUIRE);
    printf("%d",BR_NOOP);
    printf("%d",BR_SPAWN_LOOPER);
    printf("%d",BR_FINISHED);
    printf("%d",BR_DEAD_BINDER);
    printf("%d",BR_CLEAR_DEATH_NOTIFICATION_DONE);
    printf("%d",BR_FAILED_REPLY);
    return 0;
}
