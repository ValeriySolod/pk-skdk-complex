import clsx from 'clsx';
import styles from './Stepper.module.css';

export type StepperStepStatus = 'completed' | 'current' | 'upcoming' | 'error';

export interface StepperStep {
  id: string;
  label: string;
  description?: string;
  status?: StepperStepStatus;
}

export interface StepperProps {
  steps: StepperStep[];
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

const statusLabels: Record<StepperStepStatus, string> = {
  completed: 'Completed',
  current: 'Current',
  upcoming: 'Upcoming',
  error: 'Needs attention',
};

function getStepStatus(step: StepperStep): StepperStepStatus {
  return step.status ?? 'upcoming';
}

function getIndicatorContent(status: StepperStepStatus, stepNumber: number) {
  if (status === 'completed') {
    return '✓';
  }

  if (status === 'error') {
    return '!';
  }

  return stepNumber;
}

export function Stepper({
  steps,
  orientation = 'horizontal',
  className,
}: StepperProps) {
  if (steps.length === 0) {
    return null;
  }

  return (
    <nav
      className={clsx(styles.stepper, styles[orientation], className)}
      aria-label="Progress"
    >
      <ol className={styles.list}>
        {steps.map((step, index) => {
          const status = getStepStatus(step);
          const isCurrent = status === 'current';
          const stepNumber = index + 1;

          return (
            <li
              className={clsx(styles.item, styles[status])}
              key={step.id}
              aria-current={isCurrent ? 'step' : undefined}
            >
              <div className={styles.marker} aria-hidden="true">
                {getIndicatorContent(status, stepNumber)}
              </div>

              <div className={styles.content}>
                <span className={styles.status}>{statusLabels[status]}</span>
                <span className={styles.label}>{step.label}</span>
                {step.description && (
                  <span className={styles.description}>{step.description}</span>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
